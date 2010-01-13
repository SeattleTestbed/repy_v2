"""
   Author: Justin Cappos

   Start Date: 19 July 2008

   Description:

   Miscellaneous functions for the sandbox.   Random, exitall, getruntime, 
   etc.

   <Modified>
     Anthony - May 7 2009, changed the source of random data which is
     used in randomfloat. Now uses os.urandom to get random bytes,
     transforms the bytes into a random integer then uses it to
     create a float of 53bit resolution.
     Modified scheme from the random() function of the SystemRandom class,
     as defined in source code python 2.6.2 Lib/random.py
     
     Anthony - Jun 25 2009, will now use tracebackrepy.handle_internalerror
     to log when os.urandom raises a NotImplementedError.
"""

import restrictions
import nanny
import os               # for os.urandom(7)
import tracebackrepy    # for os.urandom so exception can be logged internally
import nonportable      # for getruntime
import harshexit        # for harshexit()
import threading        # for Lock()

# Public interface!
def randomfloat():
  """
   <Purpose>
     Return a random number in the range [0.0, 1.0) using sources 
     provided by the operating system (such as /dev/urandom on Unix or
     CryptGenRandom on Windows).

   <Arguments>
     None

   <Exceptions>
     None

   <Side Effects>
     This function is metered because it may involve using a hardware
     source of randomness.
     
     If os.urandom raises a NotImplementedError then we will log the
     exception as interalerror and a harshexit will occur. A machine
     that raised this exception has not been observed but it is best
     that the problemed be logged. os.urandom will raise the exception
     if a source of OS-specific random numbers is not found.

   <Returns>
     The number (a float)

  """

  restrictions.assertisallowed('randomfloat')
  nanny.tattle_quantity('random',1)
  
  # If an OS-specific source of randomness is not a found
  # a NotImplementedError would be raised. 
  # Anthony - a NotImplementedError will be logged as an internal
  # error so that we will hopefully be able to identify the system,
  # the exception is not passed on because the problem was not
  # caused by the user. The exit code 217 was chosen to be
  # unique from all other exit calls in repy.
  # Get 56 bits of random data
  try:
    randombytes = os.urandom(7)
  except NotImplementedError, e:
    tracebackrepy.handle_internalerror("os.urandom is not implemented " + \
        "(Exception was: %s)" % e.message, 217)

  
  randomint = 0L
  for i in range(0, 7):
    randomint = (randomint << 8) 
    randomint = randomint + ord(randombytes[i]) 

  # Trim off the excess bits to get 53bits
  randomint = randomint >> 3
  # randomint is a number between 0 and 2**(53) - 1
  
  return randomint * (2**(-53))


# Public interface!
def getruntime():
  """
   <Purpose>
      Return the amount of time the program has been running.   This is in
      wall clock time.   This function is not guaranteed to always return
      increasing values due to NTP, etc.

   <Arguments>
      None

   <Exceptions>
      None.

   <Side Effects>
      None

   <Remarks>
      Accurate granularity not guaranteed past 1 second.

   <Returns>
      The elapsed time as float
  """
  restrictions.assertisallowed('getruntime')
  return nonportable.getruntime()


# public interface
def exitall():
  """
   <Purpose>
      Allows the user program to stop execution of the program without
      passing an exit event to the main program. 

   <Arguments>
      None.

   <Exceptions>
      None.

   <Side Effects>
      Interactions with timers and connection / message receiving functions 
      are undefined.   These functions may be called after exit and may 
      have undefined state.

   <Returns>
      None.   The current thread does not resume after exit
  """

  restrictions.assertisallowed('exitall')

  harshexit.harshexit(200)




# public interface
def getlock():
  """
   <Purpose>
      Returns a lock object to the user program.    A lock object supports
      two functions: acquire and release.   See threading.Lock() for details

   <Arguments>
      None.

   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      The lock object.
  """

  restrictions.assertisallowed('getlock')

  # I'm a little worried about this, but it should be safe.
  return threading.Lock()


# Public interface
def get_thread_name():
  """
  <Purpose>
    Returns a string identifier for the currently executing thread.
    This identifier is unique to this thread.

  <Arguments>
    None.

  <Exceptions>
    None.

  <Side Effects>
    None.

  <Returns>
    A string identifier.
  """

  # Check if this is allows
  restrictions.assertisallowed('get_thread_name')

  # Get the thread object
  tobj = threading.currentThread()

  # Return the name
  return tobj.getName()


