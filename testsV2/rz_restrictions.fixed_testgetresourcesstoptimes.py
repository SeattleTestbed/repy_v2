"""
This unit test checks the stoptimes array returned by getresources()

We check that:
  1) Initially it is almost empty. Allow 2 entries
  2) If we start burning CPU, it should get populated
  3) If we try to use 100% CPU time, we should expect to be stopped for about
    0.9 seconds to compensate (allow for 0.8 to 1)
"""

# Get the initial values
lim, usage, init_stops = getresources()

# Check the initial length 
if len(init_stops) > 2:
  print "Initial length of stoptimes array is more than 2! Array: "+str(init_stops)

# Start burning CPU for 2 seconds
start = getruntime()
while getruntime() - start < 2:
  for x in xrange(100):
    x = x ** x

# Get the info again
lim, usage, sec_stops = getresources()

# Check that our cpu and thread CPU are at least 0.2
if usage["cpu"] < 0.2 or usage["threadcpu"] < 0.2:
  print "CPU usage too low! We should have used at least 0.2 seconds of CPU time!"

# Check the stops
if len(sec_stops) <= len(init_stops):
  print "We should have been stopped while wasting CPU!"

# Check the last entry
last_stop = sec_stops[-1]

# Check the amount is between 0.8 and 1
if last_stop[1] < 0.8:
  print "We expect to be stopped at least for 0.8 seconds! Were stopped for: "+str(last_stop[1])
if last_stop[1] > 1:
  print "We expect to be stopped at most for 1 second! Were stopped for: "+str(last_stop[1])

