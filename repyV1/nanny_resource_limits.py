# nanny_resource_limits -- A module to contain functionality needed by both
# nanny and nonportable. Functions exported:
# init:   Call immediately after import, passing nonportable.getruntime.
# calculate_cpu_sleep_interval:   Calculates sleep interval to try and meet
#   target CPU usage.
# resource_limit:   Returns the limit/availability of a resource.



# Needed for threading.Lock
import threading



# These are resources that drain / replenish over time
renewable_resources = ['cpu', 'filewrite', 'fileread', 'netsend', 'netrecv',
	'loopsend', 'looprecv', 'lograte', 'random']

# These are resources where the quantity of use may vary by use 
quantity_resources = ["cpu", "memory", "diskused", "filewrite", "fileread", 
	'loopsend', 'looprecv', "netsend", "netrecv", "lograte", 'random']

# These are resources where the number of items is the quantity (events because
# each event is "equal", insockets because a listening socket is a listening 
# socket)
fungible_item_resources = ['events', 'filesopened', 'insockets', 'outsockets']

# resources where there is no quantity.   There is only one messport 12345 and
# a vessel either has it or the vessel doesn't.   The resource messport 12345
# isn't fungible because it's not equal to having port 54321.   A vessel may
# have more than one of the resulting individual resources and so are
# stored in a list.
individual_item_resources = ['messport', 'connport']

# Include resources that are fungible vs those that are individual...
item_resources = fungible_item_resources + individual_item_resources


# This is used by restrictions.py to set up our tables
known_resources = quantity_resources + item_resources 

# Whenever a resource file is attached to a vessel, an exception should
# be thrown if these resources are not present.  If any of these are left
# unassigned, mysterious node manager errors will arise -Brent
must_assign_resources = ["cpu", "memory", "diskused"]

# The restrictions on how resources should be used.   This is filled in for
# me by the restrictions module
# keys are the all_resources, a value is a float with meaning to me...
resource_restriction_table = {}


# The current quantity of a resource that is used.   This should be updated
# by calling update_resource_consumption_table() before being used.
resource_consumption_table = {}


# Locks for resource_consumption_table
# I only need to lock the renewable resources because the other resources use
# sets (which handle locking internally)
renewable_resource_lock_table = {}
for init_resource in renewable_resources:
  renewable_resource_lock_table[init_resource] = threading.Lock()


# This lock is used to prevent race conditions for tattle_add_item and 
# tattle_remove_item.   
fungible_resource_lock_table = {}
for init_resource in fungible_item_resources:
  fungible_resource_lock_table[init_resource] = threading.Lock()


# Set up renewable resources to start now...
renewable_resource_update_time = {}


# Set up individual_item_resources to be in the restriction_table (as a set)
for init_resource in individual_item_resources:
  resource_restriction_table[init_resource] = set()



def init(getruntime):
  # Initialization function, call on import with argument nonportable.getruntime.
  global renewable_resources
  global renewable_resource_update_time

  for init_resource in renewable_resources:
    renewable_resource_update_time[init_resource] = getruntime()


########################## Used Internally for resource monitoring and metering #########

# Data structures and functions for a cross platform CPU limiter

# Debug purposes: Calculate real average
#appstart = time.time()
#rawcpu = 0.0
#totaltime = 0.0

def calculate_cpu_sleep_interval(cpulimit, percentused, elapsedtime):
  """
  <Purpose>
    Calculates proper CPU sleep interval to best achieve target cpulimit.
  
  <Arguments>
    cpulimit:
      The target cpu usage limit
    percentused:
      The percentage of cpu used in the interval between the last sample of the process
    elapsedtime:
      The amount of time elapsed between last sampling the process
  
  <Exceptions>
    ZeroDivisionError if elapsedtime is 0.
  
  <Returns>
    Time period the process should sleep
  """
  # Debug: Used to calculate averages
  #global totaltime, rawcpu, appstart

  # Return 0 if elapsedtime is non-positive
  if elapsedtime <= 0:
    return 0
    
  # Calculate Stoptime
  #  Mathematically Derived from:
  #  (PercentUsed * TotalTime) / ( TotalTime + StopTime) = CPULimit
  stoptime = max(((percentused * elapsedtime) / cpulimit) - elapsedtime , 0)

  # Print debug info
  #rawcpu += percentused*elapsedtime
  #totaltime = time.time() - appstart
  #print totaltime , "," , (rawcpu/totaltime) , "," ,elapsedtime , "," ,percentused
  #print percentused, elapsedtime
  #print "Stopping: ", stoptime

  # Return amount of time to sleep for
  return stoptime



# Armon: This is an extremely basic wrapper function, that just allows
# for pre/post processing if required in the future
def resource_limit(resource):
  """
  <Purpose>
    Returns the limit or availability of a resource.
    
  <Arguments>
    resource:
      The resource about which information is being requested.
  
  <Exceptions>
    KeyError if the resource does not exist.
    
  <Side Effects>
    None
  
  <Returns>
    The resource availability or limit.
  """
  
  return resource_restriction_table[resource]
