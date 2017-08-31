"""
This unit test checks the file.writeat() call works and returns expected data.
"""

#pragma repy

# Get a junk file
JUNK_FILE = "this.is.a.test.file.123s34"

# Open
fileh = openfile(JUNK_FILE, True)

# Try to write some data
data = "hi" * 8
fileh.writeat(data, 0)

# Try to read the string
r_data = fileh.readat(16,0)

# Check that it matches the comment at the top
if data != r_data:
  log("Data does not match! Got: "+r_data,'\n')

fileh.close()

# Remove the file
removefile(JUNK_FILE)

