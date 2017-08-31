"""
This unit test checks createlock and the lock object doing a non-blocking acquire.
"""

#pragma repy


lock = createlock()

# Exits after 2 second time out
def timeout():
  sleep(2)
  log("Timed Out!",'\n')
  exitall()

# Launch the timeout thread
createthread(timeout)

# Double acquire
acquired = lock.acquire(False)
if not acquired:
  log("First acquire should work!",'\n')

acquired_2 = lock.acquire(False)
if acquired_2:
  log("Second acquire should fail!",'\n')

# Exit now
exitall()

