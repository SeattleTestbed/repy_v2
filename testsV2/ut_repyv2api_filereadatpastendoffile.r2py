"""
This unit test checks the behavior of the file object when trying to
read past the file offset.
"""

#pragma repy

# Get a handle
fobj = openfile("repy.py",False)

# The file should be less than 100K
try:
  data = fobj.readat(8, 100000)
except SeekPastEndOfFileError:
  pass
else:
  log("Should get a seek error!",'\n')


