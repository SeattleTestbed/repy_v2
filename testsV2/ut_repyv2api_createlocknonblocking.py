"""
This unit test checks createlock and the lock object doing a non-blocking acquire.
"""

#pragma repy


lock = createlock()

# Exits after 2 second time out
def timeout():
  sleep(2)
  print "Timed Out!"
  exitall()

# Launch the timeout thread
createthread(timeout)

# Double acquire
acquired = lock.acquire(False)
if not acquired:
  print "First acquire should work!"

acquired_2 = lock.acquire(False)
if acquired_2:
  print "Second acquire should fail!"

# Exit now
exitall()

