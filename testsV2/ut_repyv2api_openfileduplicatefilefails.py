"""
This unit test checks the behavior of openfile when the file is in use.
"""

#pragma repy

# Get a handle to repy.py
fileh = openfile("repy.py",False)

# Try to get another handle
try:
  fileh2 = openfile("repy.py",False)
except FileInUseError:
  pass
else:
  log("Should get FileInUseError!",'\n')

# Close the handle
fileh.close()

# The second open should work now
fileh2 = openfile("repy.py", False)
fileh2.close()


