"""
This unit test checks the removefile API.

We check that:
  1) We get an error calling with invalid arguments
  2) We get FileNotFoundError if the file does not exist
  3) We create a file, should appear in listfiles()
  4) We cannot remove a file while the handle is still open
  5) We remove that file, should not appear in listfiles()
"""

#pragma repy

FILE_NAME = "removefile.z_testremovefile.py"

# Check for the file we will create/delete
if FILE_NAME in listfiles():
  # Try to remove now
  removefile(FILE_NAME)

if FILE_NAME in listfiles():
  log("File should not exist, we just checked and removed the file!",'\n')


# We should get a FileNotFoundError now
try:
  removefile(FILE_NAME)
except FileNotFoundError:
  pass
else:
  log("Did not get an error deleting a file which does not exist!",'\n')


# Try to create the file
fileh = openfile(FILE_NAME, True)

# This should create it
if FILE_NAME not in listfiles():
  log("File should exist, we just created it!",'\n')


# Try to remove it
try:
  removefile(FILE_NAME)
except FileInUseError:
  pass
else:
  log("We should get a FileInUseError!",'\n')


# Close the handle, then remove the file
fileh.close()
removefile(FILE_NAME)

# Now, it should be gone
if FILE_NAME in listfiles():
  log("File should not exist, we just deleted it!",'\n')


# Function to try various bad arguments
def tryit(arg):
  try:
    removefile(arg)
  except RepyArgumentError:
    pass
  else:
    log("removefile on '"+str(arg)+"' should fail. Worked.",'\n')

# Check some random arguments
tryit(123)
tryit(None)
tryit(3.1415)
tryit(".")
tryit("..")
tryit("dir/file")


