"""
   Author: Justin Cappos

   Start Date: 29 June 2008

   Description:

   Timer functions for the sandbox.   This does sleep as well as setting and
   cancelling timers.
"""

import threading
import thread # Armon: this is to catch thread.error
import nanny
import idhelper

# This is to use do_sleep
import misc

# for printing exceptions
import tracebackrepy

# for harshexit
import harshexit

# Import the exception hierarchy
from exception_hierarchy import *

##### Constants

# Armon: Prefix for use with event handles
EVENT_PREFIX = "_EVENT:"

# Store callable
safe_callable = callable


##### Public Functions

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
  # Use the do_sleep implementation in misc
  misc.do_sleep(seconds)


def createthread(function):
  """
  <Purpose>
    Creates a new thread of execution.

  <Arguments>
    function:
      The function to invoke on entering the new thread.

  <Exceptions>
    RepyArgumentError is raised if the function is not callable.
    ResourceExhaustedError is raised if there are no available events.

  <Side Effects>
    Launches a new thread.

  <Resource Consumption>
    Consumes an event.

  <Returns>
    None
  """
  # Check if the function is callable
  if not safe_callable(function):
    raise RepyArgumentError("Provided function is not callable!")

  # Generate a unique handle and see if there are resources available
  eventhandle = EVENT_PREFIX + idhelper.getuniqueid()
  nanny.tattle_add_item('events', eventhandle)

  # Wrap the provided function
  def wrapped_func():
    try:
      function()
    except:
      # Exit if they throw an uncaught exception
      tracebackrepy.handle_exception()
      harshexit.harshexit(30)
    finally: 
      # Remove the event before I exit
      nanny.tattle_remove_item('events',eventhandle)

  # Create a thread object
  tobj = threading.Thread(target=wrapped_func, name=idhelper.get_new_thread_name(EVENT_PREFIX))

  # Check if we get an exception trying to create a new thread
  try:
    tobj.start()
  except thread.error:
    # Set exit code 56, which stands for a Threading Error
    # The Node manager will detect this and handle it
    harshexit.harshexit(56)
 
