"""
This unit test checks the file.readat() argument.

We check:
  1) Input sanity checking
  2) SeekPastEndOfFile is raised
"""

#pragma repy

def tryit(sizelimit, offset):
  try:
    fileh.readat(sizelimit, offset)
  except RepyArgumentError:
    pass
  else:
    log("Readat with sizelimit: "+str(sizelimit)+" and offset: "+str(offset)+" should have error!",'\n')

# Open a file
fileh = openfile("repy.py", False)

# Try some stuff
tryit(-1,0)
tryit(0,-1)
tryit(False, 0)
tryit(1, None)

# Try to seek past the end
try:
  fileh.readat(8, 500000)
  log("Read past then EOF!",'\n')
except SeekPastEndOfFileError:
  pass

# Close the file
fileh.close()



