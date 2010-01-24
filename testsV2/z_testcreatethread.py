"""
This unit test checks the 'createthread' API call.

We check:
  1) Input sanity
  2) If another thread is actually launched
  3) getresources shows that the event count went up and back down
"""

# Get the initial resource usage
lim, init_usage, stoptimes = getresources()

# This flag is set to True by the second thread
FLAG = [False]

# Function for the second thread
def secondthread():
  # Set the flag
  FLAG[0] = True

  # Check that the event count went up
  lim, sec_usage, stoptimes = getresources()

  if sec_usage["events"] != init_usage["events"]+1:
    print "Event accounting is incorrect! Reports:"+str(sec_usage["events"])


# Check for input sanity
try:
  createthread(None)
  print "Bad input accepted!"
except RepyArgumentError:
  pass

# Start the second thread
createthread(secondthread)

# Wait a second
sleep(1)

# Check the flag
if not FLAG[0]:
  print "Second thread not launched! Flag is still false!"

# Check that the event count is back to the init
lim, third_usage, stoptimes = getresources()

if third_usage["events"] != init_usage["events"]:
  print "Event account is incorrect! Not restored to original value!"

