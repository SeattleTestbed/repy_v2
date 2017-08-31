"""
This unit test checks the behavior of a file object after
being closed.

"""

#pragma repy

# Get a file
fileh = openfile("repy.py", False)

# Close the file
fileh.close()

# All other operations should raise an error
try:
  fileh.readat(1,0)
  log("Read after close!",'\n')
except FileClosedError:
  pass

try:
  fileh.writeat("",0)
  log("Wrote after close!",'\n')
except FileClosedError:
  pass

try:
  fileh.close()
  log("Closed after close!",'\n')
except FileClosedError:
  pass

