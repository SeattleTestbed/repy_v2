"""
This unit test checks the 'sleep' call.
"""

#pragma repy

try:
  sleep("abc")
  print "Error! Accepted bad input!"
except:
  pass

# Get the runtime
start = getruntime()

sleep(1)

# Get the runtime again
end = getruntime()

if end - start < 1:
  print "Slept for less than 1 second!"

if end - start > 1.5:
  print "Slept for more than 1.5 seconds!"


