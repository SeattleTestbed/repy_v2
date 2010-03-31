"""
This unit test checks the 'sleep' call.
"""

#pragma repy

try:
  sleep("abc")
  log("Error! Accepted bad input!",'\n')
except:
  pass

# Get the runtime
start = getruntime()

sleep(1)

# Get the runtime again
end = getruntime()

if end - start < 1:
  log("Slept for less than 1 second!",'\n')

if end - start > 1.5:
  log("Slept for more than 1.5 seconds!",'\n')


