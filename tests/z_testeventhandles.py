# Armon: The test tries to test canceltimer and settimer (to a lesser degree)
# We check for a proper prefix, and we test the behavior of canceltimer
# with various handles, valid, invalid, and pseudo-valid
#


def noop(*args):
  pass

def dumpmesg():
  print "Hi!"

# Try canceltimer with a handle, expects failure
def tryjunk(handle):
  try:
    canceltimer(handle)
  except:
    pass
  else:
    print "Expected canceltimer to fail with handle:",handle

if callfunc == "initialize":
  # Try to set 2 timers
  handle1 = settimer(20,dumpmesg,())
  handle2 = settimer(20,dumpmesg,())

  # We should be able to use cancel timer with these handles
  val1 = canceltimer(handle1)
  val2 = canceltimer(handle2)

  if not (val1 and val2):
    print "Canceltimer unexpectedly failed. Handle 1 stop:",val1,"Handle 2 stop:",val2

  # Try some junk handles
  tryjunk(1)
  tryjunk(5L)
  tryjunk(5.0)
  tryjunk("Hi!")
  tryjunk(None)
  tryjunk(True)

  # Get a handle from recvmess
  waith = recvmess(getmyip(),<messport>,noop)

  # Try canceling this
  tryjunk(waith)
  stopcomm(waith)
 
  # Try stopping the handles we already stopped
  val2 = canceltimer(handle1)
  val3 = canceltimer(handle2)

  if val2 or val3:
    print "Was able to stop an already stopped event! Handle 1 stop:",val3,"Handle 2 stop:",val4

  # Test pseudo-valid handles
  # This is an invalid argument according to the namespace layer.
  #if canceltimer("_EVENT:JUNKHANDLE"):
  #  print "A junk pseudo-handle was able to stop an event!"


