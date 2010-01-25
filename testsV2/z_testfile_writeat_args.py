"""
This unit test checks the file.writeat() argument.

We check:
  1) Input sanity checking
  2) SeekPastEndOfFile is raised
"""

def tryit(data, offset):
  try:
    fileh.writeat(data, offset)
  except RepyArgumentError:
    pass
  else:
    print "Writeat with data: "+str(data)+" and offset: "+str(offset)+" should have error!"

# Open a file
JUNK_FILE = "this.is.a.test.junk.file.123v912"
fileh = openfile(JUNK_FILE, True)

# Try some stuff
tryit("test",-1)
tryit("test",None)
tryit(None, 0)
tryit(1, 0)

# Try to seek past the end
try:
  fileh.writeat("test", 500000)
  print "Write past then EOF!"
except SeekPastEndOfFileError:
  pass

# Close the file
fileh.close()

# Remove the file
removefile(JUNK_FILE)

