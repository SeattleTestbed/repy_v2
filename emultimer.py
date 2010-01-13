"""
   Author: Justin Cappos

   Start Date: 29 June 2008

   Description:

   Timer functions for the sandbox.   This does sleep as well as setting and
   cancelling timers.
"""

import threading
import thread # Armon: this is to catch thread.error
import time
import restrictions
import nanny
import idhelper

# This is to use do_sleep
import misc

# for printing exceptions
import tracebackrepy

# for harshexit
import harshexit


timerinfo = {}
# Table of timer structures:
# {'timer':timerobj,'function':function}

# Armon: Prefix for use with event handles
EVENT_PREFIX = "_EVENT:"

# Generates a valid event handle
def generate_eventhandle():
  """
  <Purpose>
    Generates a string event handle that can be used to uniquely identify an event.
    It is formatted so that cursory verification can be performed.

  <Returns>
    A string event handle.
  """
  # Get a unique handle from idhelper
  uniqueh = idhelper.getuniqueid()

  # Return the unique handle prefixed with EVENT_PREFIX
  return (EVENT_PREFIX + uniqueh)


# Helps validate an event handle
def is_valid_eventhandle(eventhandle):
  """
  <Purpose>
    Determines if a given event handle is valid.
    This does not guarantee validity, just proper form.

  <Arguments>
    eventhandle:
      The event handle to be checked.

  <Returns>
    True if valid, False otherwise.
  """
  # The handle must be a string, check type first
  if type(eventhandle) != str:
    return False

  # Check if the handle has the correct prefix
  return eventhandle.startswith(EVENT_PREFIX)


# Public interface!
def sleep(seconds):
  """
   <Purpose>
      Allow the current event to pause execution (similar to time.sleep()).
      This function will not return early for any reason

   <Arguments>
      seconds:
         The number of seconds to sleep.   This can be a floating point value

   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      None.
  """

  restrictions.assertisallowed('sleep',seconds)
  
  # Use the do_sleep implementation in misc
  misc.do_sleep(seconds)



# Public interface!
def settimer(waittime, function, args):
  """
   <Purpose>
      Allow the current event to set an event to be performed in the future.
      This does not guarantee the event will be triggered at that time, only
      that it will be triggered after that time.

   <Arguments>
      waittime:
         The minimum amount of time to wait before delivering the event
      function:
         The function to call
      args:
         The arguments to pass to the function.   This should be a tuple or 
         list

   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      A timer handle, for use with canceltimer
  """
  restrictions.assertisallowed('settimer',waittime)
  
  eventhandle = generate_eventhandle()

  nanny.tattle_add_item('events',eventhandle)

  tobj = threading.Timer(waittime,functionwrapper,[function] + [eventhandle] + [args])

  # Set the name of the thread
  tobj.setName(idhelper.get_new_thread_name(EVENT_PREFIX))

  timerinfo[eventhandle] = {'timer':tobj}
  
  # Check if we get an exception trying to create a new thread
  try:
    # start the timer
    tobj.start()
  except thread.error, exp:
    # Set exit code 56, which stands for a Threading Error
    # The Node manager will detect this and handle it
    harshexit.harshexit(56)
  
  return eventhandle
  

# Private function.   This exists to allow me to do quota based items
def functionwrapper(func, timerhandle, args):
  #restrictions ?
  # call the function with the arguments
  try:
    if timerhandle in timerinfo:
      del timerinfo[timerhandle]
    else:
      # I've been "stopped" by canceltimer
      return
  except KeyError:
    # I've been "stopped" by canceltimer
    return
    
  try:
    func(*args)
  except:
    # Exit if they throw an uncaught exception
    tracebackrepy.handle_exception()
    harshexit.harshexit(30)
    
  # remove the event before I exit
  nanny.tattle_remove_item('events',timerhandle)
  



# Public interface!
def canceltimer(timerhandle):
  """
   <Purpose>
      Cancels a timer.

   <Arguments>
      timerhandle:
         The handle of the timer that should be stopped.   Handles are 
         returned by settimer

   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      If False is returned, the timer already fired or was cancelled 
      previously.   If True is returned, the timer was cancelled
  """

  restrictions.assertisallowed('canceltimer')

  # Armon: Check that the given handle is valid
  if not is_valid_eventhandle(timerhandle):
    raise Exception("Invalid timer handle specified!")

  try:
    timerinfo[timerhandle]['timer'].cancel()
  except KeyError:
    # The timer already fired (or was cancelled)
    return False

  try:
    del timerinfo[timerhandle]
  except KeyError:
    # The timer just fired (or was cancelled)
    return False
  else:
    # I was able to delete the entry, the function will abort.   I can remove
    # the event
    nanny.tattle_remove_item('events',timerhandle)
    return True
    
