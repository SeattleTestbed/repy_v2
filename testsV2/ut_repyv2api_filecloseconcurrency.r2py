"""
This unit test checks the behavior of the fileobject when
close is called concurrently with a read/write.
"""

#pragma repy

JUNK_FILE = "test.write.junk.data"

def closeit():
  sleep(0.1)
  junkh.close()

# Get a handle to a junk file
junkh = openfile(JUNK_FILE, True)

# Try to write a lot of data, 150K bytes should take .5 seconds
data = "--Is 15 bytes.\n" * 10000

createthread(closeit)
junkh.writeat(data, 0)

# The file should be closed now
try:
  junkh.readat(15, 0)
  log("Read worked after close!",'\n')
except FileClosedError:
  pass


# Open a handle to read now
junkh = openfile(JUNK_FILE, False)

# Try to read back all 150K bytes, should take .5 seconds
createthread(closeit)
data = junkh.readat(150000, 0)

# All the data should be read
if len(data) != 150000:
  log("Read less data than expected!",'\n')

# It should be closed now
try:
  junkh.readat(15, 0)
  log("Read worked after close! (2)",'\n')
except FileClosedError:
  pass


# Remove the file
removefile(JUNK_FILE)

