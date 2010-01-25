# DO NOT REMOVE
"""
This unit test checks the file.readat() call works and returns expected data.
"""

# Open ourself
fileh = openfile("z_testfile_readat_basic.py", False)

# Try to read the string at the top
data = fileh.readat(14, 2)

# Check that it matches the comment at the top
if data != "DO NOT REMOVE\n":
  print "Data does not match! Got: "+data

fileh.close()

