# DO NOT REMOVE
"""
This unit test checks the file.readat() call works and returns expected data.
"""

#pragma repy

# Open ourself
fileh = openfile("ut_repyv2api_filereadatbasictest.py", False)

# Try to read the string at the top
data = fileh.readat(14, 2)

# Check that it matches the comment at the top
if data != "DO NOT REMOVE\n":
  log("Data does not match! Got: "+data,'\n')

fileh.close()

