"""

This unit test checks the resource consumption of openfile.

We check for:
  1) 4K file read on open
  2) 4K file write on open w/create
"""

#pragma repy

# Get a file which does not exist
BAD_FILE = "random.junk.file.does.not.exist"

# If that actually exists... Pick a different name
while BAD_FILE in listfiles():
  BAD_FILE += ".abc"


# Get the baseline fileread usage
lim, baseline, stops = getresources()

try:
  openfile(BAD_FILE, False)
except FileNotFoundError:
  # Check the usage again
  lim, after_check, stops = getresources()

  # We should have used about an extra 4096.
  # Less is possible since it may have been restored
  if after_check["fileread"] - baseline["fileread"] < 4000:
    log("We should have used 4096 more fileread! After: "+str(after_check["fileread"])+" Before: "+str(baseline["fileread"]),'\n')

else:
  log("Opened handle to file that does not exist: "+str(BAD_FILE),'\n')
  exitall()

# Create the file, this should work
openfile(BAD_FILE, True)

# Get the usage now
lim, after_create, stops = getresources()

# Check that it exists
if BAD_FILE not in listfiles():
  log("File should exist! It was just created!",'\n')

# Remove the file
removefile(BAD_FILE)

# We should now use 4096 file write, plus more fileread
if after_create["filewrite"] != 4096:
  log("File write should be 4096! Is: "+str(after_create["filewrite"]),'\n')
if after_create["fileread"] - after_check["fileread"] < 4000:
  log("We should have used 4096 more fileread after create! Used: "+str(after_create["fileread"]) + " Before: "+str(after_check["fileread"]),'\n')

