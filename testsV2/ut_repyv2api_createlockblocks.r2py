"""
This unit test checks createlock and the lock object doing a blocking acquire.
"""

#pragma repy

lock = createlock()

# Sleeps for .5 seconds and unlocks the global "lock" object
def thread():
  sleep(0.5)
  _context["lock"].release()

# Exits after 2 second time out
def timeout():
  sleep(2)
  log("Timed Out!",'\n')
  exitall()

# Launch the timeout thread, then the unlock thread
createthread(timeout)
createthread(thread)

# Double acquire
lock.acquire(True)
lock.acquire(True)

# Exit now
exitall()

