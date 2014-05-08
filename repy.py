""" 
<Author>
  Justin Cappos
  Ivan Beschastnikh (12/24/08) -- added usage
  Brent Couvrette   (2/27/09) -- added servicelog commandline option
  Conrad Meyer (5/22/09) -- switch option parsing to getopt
  Moshe Kaplan (8/15/12) -- switched option parsing to optparse

<Start Date>
  June 26th, 2008

<Description>
  Restricted execution environment for python.  Should stop someone
  from doing "bad things" (which is also defined to include many
  useful things).  This module allows the user to define code that
  gets called either on the receipt of a packet, when a timer fires,
  on startup, and on shutdown.  The restricted code can only do a few
  "external" things like send data packets and store data to disk.
  The CPU, memory, disk usage, and network bandwidth are all limited.

<Usage>
  Usage: repy.py [options] resourcefn program_to_run.r2py [program args]

  Where [options] are some combination of the following:

  --ip IP                : This flag informs Repy that it is allowed to bind to the given given IP.
                         : This flag may be asserted multiple times.
                         : Repy will attempt to use IP's and interfaces in the order they are given.
  --execinfo             : Display information regarding the current execution state. 
  --iface interface      : This flag informs Repy that it is allowed to bind to the given interface.
                         : This flag may be asserted multiple times.
  --nootherips           : Instructs Repy to only use IP's and interfaces that are explicitly given.
                         : It should be noted that loopback (127.0.0.1) is always permitted.
  --logfile filename.txt : Set up a circular log buffer and output to logfilename.txt
  --stop filename        : Repy will watch for the creation of this file and abort when it happens
                         : File can have format EXITCODE;EXITMESG. Code 44 is Stopped and is the default.
                         : EXITMESG will be printed prior to exiting if it is non-null.
  --status filename.txt  : Write status information into this file
  --cwd dir              : Set Current working directory
  --servicelog           : Enable usage of the servicelogger for internal errors
"""



import os
import sys
import time
import optparse
import threading

# Relative imports

# First make sure the version of python is supported
import checkpythonversion
checkpythonversion.ensure_python_version_is_supported()

import safe
import nanny
import emulcomm
import idhelper
import harshexit
import namespace
import nonportable
import loggingrepy
import statusstorage
import repy_constants
import nmstatusinterface

# Armon: Using VirtualNamespace as an abstraction around direct execution
import virtual_namespace

## we'll use tracebackrepy to print our exceptions
import tracebackrepy

from exception_hierarchy import *

# BAD: REMOVE these imports after we remove the API calls
#import emulfile
import emulmisc
#import emultimer

# Disables safe, and resumes normal fork
def nonSafe_fork():
  val = __orig_fork()
  if val == 0 and safe._builtin_globals_backup != None:
    safe._builtin_restore()
  return val

# Only override fork if it exists (e.g. Windows)
if "fork" in dir(os):  
  __orig_fork = os.fork
  os.fork = nonSafe_fork



def get_safe_context(args):


  # These will be the functions and variables in the user's namespace (along
  # with the builtins allowed by the safe module).
  usercontext = {'mycontext':{}}
  
  # Add to the user's namespace wrapped versions of the API functions we make
  # available to the untrusted user code.
  namespace.wrap_and_insert_api_functions(usercontext)

  # Convert the usercontext from a dict to a SafeDict
  usercontext = safe.SafeDict(usercontext)

  # Allow some introspection by providing a reference to the context
  usercontext["_context"] = usercontext

  # BAD:REMOVE all API imports
  usercontext["getresources"] = nonportable.get_resources
  #usercontext["openfile"] = emulfile.emulated_open
  #usercontext["listfiles"] = emulfile.listfiles
  #usercontext["removefile"] = emulfile.removefile
  #usercontext["exitall"] = emulmisc.exitall
  #usercontext["createlock"] = emulmisc.createlock
  #usercontext["getruntime"] = emulmisc.getruntime
  #usercontext["randombytes"] = emulmisc.randombytes
  #usercontext["createthread"] = emultimer.createthread
  #usercontext["sleep"] = emultimer.sleep
  #usercontext["getthreadname"] = emulmisc.getthreadname
  usercontext["createvirtualnamespace"] = virtual_namespace.createvirtualnamespace
  usercontext["getlasterror"] = emulmisc.getlasterror
      
  # call the initialize function
  usercontext['callfunc'] = 'initialize'
  usercontext['callargs'] = args[:]


  return usercontext




def execute_namespace_until_completion(thisnamespace, thiscontext):

  # I'll use this to detect when the program is idle so I know when to quit...
  idlethreadcount =  threading.activeCount()

 
  # add my thread to the set of threads that are used...
  event_id = idhelper.getuniqueid()
  try:
    nanny.tattle_add_item('events', event_id)
  except Exception, e:
    tracebackrepy.handle_internalerror("Failed to acquire event for '" + \
              "initialize' event.\n(Exception was: %s)" % e.message, 140)
 
  
  try:
    thisnamespace.evaluate(thiscontext)
  except SystemExit:
    raise
  except:
    # I think it makes sense to exit if their code throws an exception...
    tracebackrepy.handle_exception()
    harshexit.harshexit(6)
  finally:
    nanny.tattle_remove_item('events', event_id)

  # I've changed to the threading library, so this should increase if there are
  # pending events
  while threading.activeCount() > idlethreadcount:
    # do accounting here?
    time.sleep(0.25)

  # Once there are no more events, return...
  return

def init_repy_location(repy_directory):
  
  # Translate into an absolute path
  if os.path.isabs(repy_directory):
    absolute_repy_directory = repy_directory
  
  else:
    # This will join the currect directory with the relative path
    # and then get the absolute path to that location
    absolute_repy_directory = os.path.abspath(os.path.join(os.getcwd(), repy_directory))
  
  # Store the absolute path as the repy startup directory
  repy_constants.REPY_START_DIR = absolute_repy_directory
 
  # For security, we need to make sure that the Python path doesn't change even
  # if the directory does...
  newsyspath = []
  for item in sys.path[:]:
    if item == '' or item == '.':
      newsyspath.append(os.getcwd())
    else:
      newsyspath.append(item)

  # It should be safe now.   I'm assuming the user isn't trying to undercut us
  # by setting a crazy python path
  sys.path = newsyspath


def add_repy_options(parser):
  """Adds the Repy command-line options to the specified optparser
  """

  parser.add_option('--ip',
                    action="append", type="string", dest="ip" ,
                    help="Explicitly allow Repy to bind to the specified IP. This option can be used multiple times."
                    )
  parser.add_option('--execinfo',
                    action="store_true", dest="execinfo", default=False,
                    help="Display information regarding the current execution state."
                    )
  parser.add_option('--iface',
                    action="append", type="string", dest="interface",
                    help="Explicitly allow Repy to bind to the specified interface. This option can be used multiple times."
                    )
  parser.add_option('--nootherips',
                    action="store_true", dest="nootherips",default=False,
                    help="Do not allow IPs or interfaces that are not explicitly specified"
                    )
  parser.add_option('--logfile',
                    action="store", type="string", dest="logfile",
                    help="Set up a circular log buffer and output to logfile"
                    )
  parser.add_option('--stop',
                    action="store", type="string", dest="stopfile",
                    help="Watch for the creation of stopfile and abort when it is created"
                    )
  parser.add_option('--status',
                    action="store", type="string", dest="statusfile",
                    help="Write status information into statusfile"
                    )
  parser.add_option('--cwd',
                    action="store", type="string", dest="cwd",
                    help="Set Current working directory to cwd"
                    )
  parser.add_option('--servicelog',
                    action="store_true", dest="servicelog",
                    help="Enable usage of the servicelogger for internal errors"
                    )
    
def parse_options(options):
  """ Parse the specified options and initialize all required structures
  Note: This modifies global state, specifically, the emulcomm module
  """
  if options.ip:
    emulcomm.user_ip_interface_preferences = True

    # Append this ip to the list of available ones if it is new
    for ip in options.ip:
      if (True, ip) not in emulcomm.user_specified_ip_interface_list:
        emulcomm.user_specified_ip_interface_list.append((True, ip))

  if options.interface:
    emulcomm.user_ip_interface_preferences = True
      
    # Append this interface to the list of available ones if it is new
    for interface in options.interface:
      if (False, interface) not in emulcomm.user_specified_ip_interface_list:
        emulcomm.user_specified_ip_interface_list.append((False, interface))

  # Check if they have told us to only use explicitly allowed IP's and interfaces
  if options.nootherips:
    # Set user preference to True
    emulcomm.user_ip_interface_preferences = True
    # Disable nonspecified IP's
    emulcomm.allow_nonspecified_ips = False
    
  # set up the circular log buffer...
  # Armon: Initialize the circular logger before starting the nanny
  if options.logfile:
    # time to set up the circular logger
    loggerfo = loggingrepy.circular_logger(options.logfile)
    # and redirect err and out there...
    sys.stdout = loggerfo
    sys.stderr = loggerfo
  else:
    # let's make it so that the output (via print) is always flushed
    sys.stdout = loggingrepy.flush_logger(sys.stdout)
    
  # We also need to pass in whether or not we are going to be using the service
  # log for repy.  We provide the repy directory so that the vessel information
  # can be found regardless of where we are called from...
  tracebackrepy.initialize(options.servicelog, repy_constants.REPY_START_DIR)

  # Set Current Working Directory
  if options.cwd:
    os.chdir(options.cwd)

  # Update repy current directory
  repy_constants.REPY_CURRENT_DIR = os.path.abspath(os.getcwd())

  # Initialize the NM status interface
  nmstatusinterface.init(options.stopfile, options.statusfile)
  
  # Write out our initial status
  statusstorage.write_status("Started")




def initialize_nanny(resourcefn):
  # start the nanny up and read the resource file.  
  # JAC: Should this take a string instead?
  nanny.start_resource_nanny(resourcefn)

  # now, let's fire up the cpu / disk / memory monitor...
  nonportable.monitor_cpu_disk_and_mem()

  # JAC: I believe this is needed for interface / ip-based restrictions
  emulcomm.update_ip_cache()



def main():
  # JAC: This function should be kept as stable if possible.   Others who
  # extend Repy may be doing essentially the same thing in their main and
  # your changes may not be reflected there!


  # Armon: The CMD line path to repy is the first argument
  repy_location = sys.argv[0]

  # Get the directory repy is in
  repy_directory = os.path.dirname(repy_location)
  
  init_repy_location(repy_directory)
  

  ### PARSE OPTIONS.   These are command line in our case, but could be from
  ### anywhere if this is repurposed...
  usage = "USAGE: repy.py [options] resource_file program_to_run.r2py [program args]"
  parser = optparse.OptionParser(usage=usage)
  add_repy_options(parser)
  options, args = parser.parse_args()
  
  if len(args) < 2:
    print "Repy requires a resource file and the program to run!"
    parser.print_help()
    sys.exit(1)
  
  resourcefn = args[0]
  progname = args[1]
  progargs = args[2:]
  
  # Do a huge amount of initialization.
  parse_options(options)
  
  ### start resource restrictions, etc. for the nanny
  initialize_nanny(resourcefn)

  # Read the user code from the file
  try:
    filehandle = open(progname)
    usercode = filehandle.read()
    filehandle.close()
  except:
    print "FATAL ERROR: Unable to read the specified program file: '%s'" % (progname)
    sys.exit(1)

  # create the namespace...
  try:
    newnamespace = virtual_namespace.VirtualNamespace(usercode, progname)
  except CodeUnsafeError, e:
    print "Specified repy program is unsafe!"
    print "Static-code analysis failed with error: "+str(e)
    harshexit.harshexit(5)

  # allow the (potentially large) code string to be garbage collected
  del usercode



  # Insert program log separator and execution information
  if options.execinfo:
    print '=' * 40
    print "Running program:", progname
    print "Arguments:", progargs
    print '=' * 40



  # get a new namespace
  newcontext = get_safe_context(progargs)

  # one could insert a new function for repy code here by changing newcontext 
  # to contain an additional function.

  # run the code to completion...
  execute_namespace_until_completion(newnamespace, newcontext)

  # No more pending events for the user thread, we exit
  harshexit.harshexit(0)



if __name__ == '__main__':
  try:
    main()
  except SystemExit:
    harshexit.harshexit(4)
  except:
    tracebackrepy.handle_exception()
    harshexit.harshexit(3)
