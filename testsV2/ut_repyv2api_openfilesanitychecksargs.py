"""

This unit test checks the handling of arguments in openfile.

We check for:
  1) Handling of invalid names
  2) Handling of files that do not exist
  3) Creating a file that does not exist
"""

#pragma repy

def tryit(arg, create=False):
  try:
    openfile(arg, create)
  except RepyArgumentError:
    pass
  else:
    log("openfile worked with bad file name: '"+str(arg)+"'",'\n')

tryit(".")
tryit("..")
tryit("\t\n")
tryit(123)
tryit("a" * 121)
tryit("dir/file")
tryit(".testfile")
tryit("...")
tryit("TESTFILE")

tryit("valid-filename", 123)
tryit("valid-filename", None)


# Get a file which does not exist
BAD_FILE = "random.junk.file.does.not.exist"

# If that actually exists... Pick a different name
while BAD_FILE in listfiles():
  BAD_FILE += ".abc"

try:
  openfile(BAD_FILE, False)
except FileNotFoundError:
  pass
else:
  log("Opened handle to file that does not exist: "+str(BAD_FILE),'\n')

# Create the file, this should work
openfile(BAD_FILE, True)

# Check that it exists
if BAD_FILE not in listfiles():
  log("File should exist! It was just created!",'\n')

# Remove the file
removefile(BAD_FILE)


