"""

This unit test checks the resource consumption of openfile.

We check for:
  1) 4K fileread on open without create
  2) 4K fileread and 4K filewrite on open w/create
"""

#pragma repy

# Get a file which does not exist
BAD_FILE = "random.junk.file.does.not.exist"

# If that actually exists... Pick a different name
while BAD_FILE in listfiles():
  BAD_FILE += ".abc"

# Clear any resources used from calls to listfiles()
sleep(0.5)

try:
  openfile(BAD_FILE, False)
except FileNotFoundError:
  # Check the usage
  lim, after_check, stops = getresources()

  # We should have used 4096 fileread.
  if after_check["fileread"] != 4096:
    log("We should have used 4096 fileread! Used: " + str(after_check["fileread"]) + "\n")

else:
  log("Opened handle to file that does not exist: "+str(BAD_FILE),'\n')
  exitall()

# Clear any resources used from previous calls
sleep(0.5)

# Create the file, this should work
openfile(BAD_FILE, True)

# Get the usage now. We don't want the later listfiles() to ruin our measurement
lim, after_create, stops = getresources()

# Verify that the file exists
if BAD_FILE not in listfiles():
  log("File should exist! It was just created!",'\n')

# Remove the file
removefile(BAD_FILE)

# We should have used 4096 filewrite, 4096 fileread
if after_create["filewrite"] != 4096:
  log("File write should be 4096! Used: "+str(after_create["filewrite"]),'\n')
if after_create["fileread"] != 4096:
  log("We should have used 4096 fileread after create! Used: "+str(after_create["fileread"]) + '\n')

