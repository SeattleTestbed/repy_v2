#!python
"""
<Program>
  servicelogger.py

<Date Started>
  January 24th, 2008

<Author>
  Brent Couvrette
  couvb@cs.washington.edu

<Purpose>
  Module abstracting away service logging.  Other modules simply have to call
  log with the name of the log file they wish to write to, and the
  servicelogger will write their message with time and pid stamps to the
  service vessel.  init must be called before log.
"""

import os
import loggingrepy_core
import time
import persist
# we need to get and process exception information
import sys
import traceback

# We don't import from repyportability because when this is imported from
# within repy, restrictions files are no longer honored.

from repyportability import *
_context = locals()
add_dy_support(_context)

dy_import_module_symbols('servicelookup.repy')



logfile = None
servicevessel = None


def get_servicevessel(maindirectory = '.', readattempts = 3):
  """
  <Purpose>
    Get the service vessel directory using vesseldict. 
    
  <Arguments>
    maindirectory:   This is the directory where repy.py, vesseldict, etc.
                     are stored.   The default is the current directory.

    readattempts:    The number of times to attempt to read vesseldict.
                     Default is 3.
             
  <Exceptions>
    TypeError if maindirectory is not a string
    Exception if reading vesseldict fails (previously recieved OSError
      from persist.py)
        
  <Side Effects>
    None
    
  <Returns>
    The service vessel.  If there is more than one,
    return the "first one" in the vesseldict (note this is a dictionary and
    so the order will be consistent but with little meaning).  If there is no 
    service vessel, return '.'
  """

  global servicevessel
  
  # this is the public key for seattle
  ownerkey = "22599311712094481841033180665237806588790054310631222126405381271924089573908627143292516781530652411806621379822579071415593657088637116149593337977245852950266439908269276789889378874571884748852746045643368058107460021117918657542413076791486130091963112612854591789518690856746757312472362332259277422867 12178066700672820207562107598028055819349361776558374610887354870455226150556699526375464863913750313427968362621410763996856543211502978012978982095721782038963923296750730921093699612004441897097001474531375768746287550135361393961995082362503104883364653410631228896653666456463100850609343988203007196015297634940347643303507210312220744678194150286966282701307645064974676316167089003178325518359863344277814551559197474590483044733574329925947570794508677779986459413166439000241765225023677767754555282196241915500996842713511830954353475439209109249856644278745081047029879999022462230957427158692886317487753201883260626152112524674984510719269715422340038620826684431748131325669940064404757120601727362881317222699393408097596981355810257955915922792648825991943804005848347665699744316223963851263851853483335699321871483966176480839293125413057603561724598227617736944260269994111610286827287926594015501020767105358832476708899657514473423153377514660641699383445065369199724043380072146246537039577390659243640710339329506620575034175016766639538091937167987100329247642670588246573895990251211721839517713790413170646177246216366029853604031421932123167115444834908424556992662935981166395451031277981021820123445253"
  ownerinfo = ""  

  # A TypeError should happen if maindirectory is of the wrong type
  vesseldictlocation = os.path.join(maindirectory, "vesseldict")

  vesseldictloaded = False
  for dontcare in range(0, readattempts):
    try:
      vesseldict = persist.restore_object(vesseldictlocation)
    except ValueError, e:
      # this means that the vessel doesn't exist.   Let's return the current
      # directory...
      return '.'
    except OSError:
      continue
    else:
      if type(vesseldict) is dict:
        vesseldictloaded = True
        break

  if not vesseldictloaded:
    raise Exception("Could not load vesseldict.")

  service_vessels = servicelookup_get_servicevessels(vesseldict, ownerkey, ownerinfo)
  
  # We're iterating through items that are in an arbitrary order (the order 
  # they were in the vesseldict).   We will return the first one that matches
  for service_vessel in service_vessels:

    # if the service_vessel directory exists, then return it!
    if os.path.isdir(os.path.join(maindirectory, service_vessel)):
      return service_vessel
  else:
    # no good, 
    return '.'
      
  

def init(logname,cfgdir = '.', maxbuffersize=1024*1024):
  """
  <Purpose>
    Sets up the service logger to use the given logname, and the nodeman.cfg
    is in the given directory.
    
  <Arguments>
    logname - The name of the log file, as well as the name of the process lock
              to be used in the event of multi process locking
    cfgdir - The directory containing nodeman.cfg, by default it is the current
             directory
    maxbuffersize - The size of the circular logging buffer.
             
  <Exceptions>
    Exception if there is a problem reading from cfgdir/nodeman.cfg
    
  <Side Effects>
    All future calls to log will log to the given logfile.
    
  <Returns>
    None
  """

  global logfile
  global servicevessel
  
  servicevessel = get_servicevessel(cfgdir)
  
  logfile = loggingrepy_core.circular_logger_core(servicevessel + '/' + logname, mbs = maxbuffersize)
  
  
def multi_process_log(message, logname, cfgdir):
  """
  <Purpose>
    Logs the given message to a log.  Does some trickery to make sure there
    no more than 10 logs are ever there.   If init hasn't been called, this 
    will perform the same actions.
    
  <Arguments>
    message - The message that should be written to the log.
    logname - The name to be used for the logfile.
    cfgdir - The directory that contains the vesseldict
  
  <Exceptions>
    Exception if there is a problem reading from cfgdir/nodeman.cfg or writing
    to the circular log.
      
  <Side Effects>
    The given message might be written to the log.
    
  <Returns>
    True if the message is logged.   False if the message isn't written because
    there are too many logs.
  """
  global servicevessel
  global logfile
  
  # If we've initialized, then log and continue...
  if logfile != None and servicevessel != None:
    log(message)
    return True
 
  
  if servicevessel == None:
    servicevessel = get_servicevessel(cfgdir)
  
  logcount = 0

  servicefiles = os.listdir(cfgdir + '/' + servicevessel)
  for servicefile in servicefiles:
    # Count all the log files.  There is always either a .old or .new for
    # every log
    if servicefile.endswith('.old'):
      logcount = logcount + 1
    elif servicefile.endswith('.new'):
      if (servicefile[:-4] + ".old") not in servicefiles:
        # If there is a new file but no old file, we will count it
        logcount = logcount + 1

      
  if logcount >= 10:
    # If there are 10 or more logfiles already present, we don't want to create
    # another.  We'll ignore any race conditions with this because this should
    # be a rare case.   
    return False
  else:
    # set up the circular logger, log the message, and return
    logfile = loggingrepy_core.circular_logger_core(cfgdir + '/' + servicevessel + '/' + logname)
    log(message)

    return True



def log(message):
  """
  <Purpose>
    Logs the given text to the given log file inside the service directory. If 
    the logfile or servicevessel is not set, this will raise an exception.
    
  <Argument>
    message - The message to log.
    
  <Exceptions>
    ValueError if init has not been called.
    Exception if writing to the log fails somehow.
    
  <Side Effects>
    The given message is written to the circular log buffer.
    
  <Returns>
    None
  """

  if logfile == None or servicevessel == None:
    # If we don't have a current log file, let's raise an exception
    raise ValueError, "Service log must be initialized before logging (logfile:'"+str(logfile)+"', servicevessel:'"+str(servicevessel)+"')"

  logfile.write(str(time.time()) + ':PID-' + str(os.getpid()) + ':' + str(message) + '\n')




def log_last_exception():
  """
  <Purpose>
    Logs the last exception (and traceback).  If there isn't an exception, it 
    will instead log a message indicating there was no exception.
    
  <Argument>
    None.
  
  <Exceptions>
    ValueError if init has not been called.
    Exception if writing to the log fails somehow.
    
  <Side Effects>
    The exception is written to the circular log buffer.
    
  <Returns>
    None
  """

  exceptiontype, exceptionvalue, exceptiontraceback = sys.exc_info()
  # If there wasn't an exception...
  if exceptiontraceback == None:
    log('asked to log a non-existent exception')
  else:
    # otherwise, use the traceback module to format it and then write it out
    exceptionstringlist = traceback.format_exception(exceptiontype, exceptionvalue, exceptiontraceback)
    exceptionstring = ''.join(exceptionstringlist)
    log(exceptionstring)
