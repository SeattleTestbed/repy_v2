"""
   Author: Justin Cappos

   Program: nanny.py

   Start Date: 1 July 2008


   Description:

   This module handles the policy decisions and accounting to detect if there 
   is a resource violation.  The actual "stopping", etc. is done in the
   nonportable module.
"""

# for sleep
import time

# needed for cpu, disk, and memory handling
import nonportable

# needed for locking
import threading

# needed for handling internal errors
import tracebackrepy

# common functionality needed between nanny and nonportable
import nanny_resource_limits
nanny_resource_limits.init(nonportable.getruntime)

# These are resources that drain / replenish over time
renewable_resources = nanny_resource_limits.renewable_resources

# These are resources where the quantity of use may vary by use 
quantity_resources = nanny_resource_limits.quantity_resources

# These are resources where the number of items is the quantity (events because
# each event is "equal", insockets because a listening socket is a listening 
# socket)
fungible_item_resources = nanny_resource_limits.fungible_item_resources

# resources where there is no quantity.   There is only one messport 12345 and
# a vessel either has it or the vessel doesn't.   The resource messport 12345
# isn't fungible because it's not equal to having port 54321.   A vessel may
# have more than one of the resulting individual resources and so are
# stored in a list.
individual_item_resources = nanny_resource_limits.individual_item_resources

# Include resources that are fungible vs those that are individual...
item_resources = fungible_item_resources + individual_item_resources


# This is used by restrictions.py to set up our tables
known_resources = quantity_resources + item_resources 

# Whenever a resource file is attached to a vessel, an exception should
# be thrown if these resources are not present.  If any of these are left
# unassigned, mysterious node manager errors will arise -Brent
must_assign_resources = nanny_resource_limits.must_assign_resources

# The restrictions on how resources should be used.   This is filled in for
# me by the restrictions module
# keys are the all_resources, a value is a float with meaning to me...
resource_restriction_table = nanny_resource_limits.resource_restriction_table


# The current quantity of a resource that is used.   This should be updated
# by calling update_resource_consumption_table() before being used.
resource_consumption_table = nanny_resource_limits.resource_consumption_table


# Locks for resource_consumption_table
# I only need to lock the renewable resources because the other resources use
# sets (which handle locking internally)
renewable_resource_lock_table = nanny_resource_limits.renewable_resource_lock_table


# This lock is used to prevent race conditions for tattle_add_item and 
# tattle_remove_item.   
fungible_resource_lock_table = nanny_resource_limits.fungible_resource_lock_table


# Set up renewable resources to start now...
renewable_resource_update_time = nanny_resource_limits.renewable_resource_update_time


# Updates the values in the consumption table (taking the current time into 
# account)
def update_resource_consumption_table(resource):

  thetime = nonportable.getruntime()

  # I'm going to reduce all renewable resources by the appropriate amount given
  # the amount of elapsed time.

  elapsedtime = thetime - renewable_resource_update_time[resource]

  renewable_resource_update_time[resource] = thetime

  if elapsedtime < 0:
    # A negative number (likely a NTP reset).   Let's just ignore it.
    return

  # Remove the charge
  reduction = elapsedtime * resource_restriction_table[resource]
    
  if reduction > resource_consumption_table[resource]:

    # It would reduce it below zero (so put it at zero)
    resource_consumption_table[resource] = 0.0
  else:

    # Subtract some for elapsed time...
    resource_consumption_table[resource] = resource_consumption_table[resource] - reduction



# I want to wait until a resource can be used again...
def sleep_until_resource_drains(resource):

  # It'll never drain!
  if resource_restriction_table[resource] == 0:
    raise Exception, "Resource '"+resource+"' limit set to 0, won't drain!"
    

  # We may need to go through this multiple times because other threads may
  # also block and consume resources.
  while resource_consumption_table[resource] > resource_restriction_table[resource]:

    # Sleep until we're expected to be under quota
    sleeptime = (resource_consumption_table[resource] - resource_restriction_table[resource]) / resource_restriction_table[resource]

    time.sleep(sleeptime)

    update_resource_consumption_table(resource)







############################ Externally called ########################

def initialize_consumed_resource_tables():
  """
   <Purpose>
      Initializes the resource nanny.   Sets the resource table entries up.

   <Arguments>
      None.
         
   <Exceptions>
      None.

   <Side Effects>
      Flushes the resource consumption tables if they were already set up.

   <Returns>
      None.
  """

  # init the resource_consumption_table
  for resource in quantity_resources:
    resource_consumption_table[resource] = 0.0

  for resource in item_resources:
    # double check there is no overlap...
    if resource in quantity_resources:
      raise Exception, "Resource cannot be both quantity and item based!"

    resource_consumption_table[resource] = set()




def start_resource_nanny():
  """
   <Purpose>
      Starts a process or thread in the nanny to monitor disk, memory, and CPU

   <Arguments>
      None.
         
   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      None.
  """

  nonportable.monitor_cpu_disk_and_mem()



# let the nanny know that the process is consuming some resource
# can also be called with quantity '0' for a renewable resource so that the
# nanny will wait until there is some free "capacity"
def tattle_quantity(resource, quantity):
  """
   <Purpose>
      Notify the nanny of the consumption of a renewable resource.   A 
      renewable resource is something like CPU or network bandwidth that is 
      speficied in quantity per second.

   <Arguments>
      resource:
         A string with the resource name.   
      quantity:
         The amount consumed.   This can be zero (to indicate the program 
         should block if the resource is already over subscribed) but 
         cannot be negative

   <Exceptions>
      None.

   <Side Effects>
      May sleep the program until the resource is available.

   <Returns>
      None.
  """


  # I assume that the quantity will never be negative
  if quantity < 0:
    # This will cause the program to exit and log things if logging is
    # enabled. -Brent
    tracebackrepy.handle_internalerror("Resource '" + resource + 
        "' has a negative quantity " + str(quantity) + "!", 132)
    
  # get the lock for this resource
  renewable_resource_lock_table[resource].acquire()
  
  # release the lock afterwards no matter what
  try: 
    # update the resource counters based upon the current time.
    update_resource_consumption_table(resource)

    # It's renewable, so I can wait for it to clear
    if resource not in renewable_resources:
      # Should never have a quantity tattle for a non-renewable resource
      # This will cause the program to exit and log things if logging is
      # enabled. -Brent
      tracebackrepy.handle_internalerror("Resource '" + resource + 
          "' is not renewable!", 133)
  

    resource_consumption_table[resource] = resource_consumption_table[resource] + quantity
    # I'll block if I'm over...
    sleep_until_resource_drains(resource)
  
  finally:
    # release the lock for this resource
    renewable_resource_lock_table[resource].release()
    





def tattle_add_item(resource, item):
  """
   <Purpose>
      Let the nanny know that the process is trying to consume a fungible but 
      non-renewable resource.

   <Arguments>
      resource:
         A string with the resource name.   
      item:
         A unique identifier that specifies the resource.   It is used to
         prevent duplicate additions and removals and so must be unique for
         each item used.
         
   <Exceptions>
      Exception if the program attempts to use too many resources.

   <Side Effects>
      None.

   <Returns>
      None.
  """

  fungible_resource_lock_table[resource].acquire()

  # always unlock as we exit...
  try: 

    # It's already acquired.   This is always allowed.
    if item in resource_consumption_table[resource]:
      return

    if len(resource_consumption_table[resource]) > resource_restriction_table[resource]:
      raise InternalError, "Should not be able to exceed resource count"

    if len(resource_consumption_table[resource]) == resource_restriction_table[resource]:
      # it's clobberin time!
      raise Exception, "Resource '"+resource+"' limit exceeded!!"

    # add the item to the list.   We're done now...
    resource_consumption_table[resource].add(item)

  finally:
    fungible_resource_lock_table[resource].release()

    



def tattle_remove_item(resource, item):
  """
   <Purpose>
      Let the nanny know that the process is releasing a fungible but 
      non-renewable resource.

   <Arguments>
      resource:
         A string with the resource name.   
      item:
         A unique identifier that specifies the resource.   It is used to
         prevent duplicate additions and removals and so must be unique for
         each item used.
         
   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      None.
  """

  fungible_resource_lock_table[resource].acquire()

  # always unlock as we exit...
  try: 
    
    try:
      resource_consumption_table[resource].remove(item)
    except KeyError:
      # may happen because removal is idempotent
      pass

  finally:
    fungible_resource_lock_table[resource].release()



# used for individual_item_resources
def tattle_check(resource, item):
  """
   <Purpose>
      Check if the process can acquire a non-fungible, non-renewable resource.

   <Arguments>
      resource:
         A string with the resource name.   
      item:
         A unique identifier that specifies the resource.   It has some
         meaning to the caller (like a port number for TCP or UDP), but is 
         opaque to the nanny.   
         
   <Exceptions>
      Exception if the program attempts to use an invalid resource.

   <Side Effects>
      None.

   <Returns>
      None.
  """

  if item not in resource_restriction_table[resource]:
    raise Exception, "Resource '"+resource+" "+str(item)+"' not allowed!!!"

  resource_consumption_table[resource].add(item)
