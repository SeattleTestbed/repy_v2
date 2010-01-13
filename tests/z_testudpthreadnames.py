"""
Author: Armon Dadgar
Description:
  Tries to fire up a lot of threads and checks that all the thread names returned are unique.
  This test launches threads via incoming UDP messages, which will check that the EventDeliverer
  is working properly.
"""

# Store the names that we've already seen
THREAD_NAMES = set([])

# Allowed Events
ALLOWED_EVENTS = 9

# How many times do we re-launch all the threads?
CHECK_TIMES = 3

# Entry point for new threads
def new_mess(ip,port,mess,ch1):
  # Get our name
  name = get_thread_name()

  # Check if this name has been used before
  if name in THREAD_NAMES:
    raise Exception, "Re-used thread name '"+str(name)+"'"

  # Record this name
  else:
    THREAD_NAMES.add(name)

# Try re-using the same 9 threads 3 times
if callfunc == "initialize":
  # IP and port
  ip = getmyip()
  port = 12345

  # Setup recvmess
  recvh = recvmess(ip,port,new_mess)

  # Add our own name
  THREAD_NAMES.add(get_thread_name())

  # Run for each interval
  for round in xrange(CHECK_TIMES):
    # Launch all the threads (via messages)
    for event in xrange(ALLOWED_EVENTS):
      sendmess(ip,port,"ping")

    # Wait for the threads to terminate
    sleep(1)

  # Expected thread count is EVENTS * CHECK_TIMES + main thread
  expected = ALLOWED_EVENTS * CHECK_TIMES + 1

  if len(THREAD_NAMES) != expected:
    raise Exception,"Unexpected number of thread names! Thread names: "+str(THREAD_NAMES)
  
  # Stop listening and exit
  stopcomm(recvh)
  exitall()

