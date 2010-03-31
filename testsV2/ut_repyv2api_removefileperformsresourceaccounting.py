"""
This unit test checks the removefile API resource usage.

We check that:
  1) 4K fileread is used on success or failure
  2) 4K filewrite is used on success
"""

#pragma repy

FILE_NAME = "removefile.z_testremovefile_resources.py"

try:
  removefile(FILE_NAME)
except FileNotFoundError:
  pass
else:
  log("File: '"+FILE_NAME+"' should not exist!",'\n')

lim, usage, stops = getresources()
if usage["fileread"] != 4096:
  log("File read should be 4096! Usage: "+str(usage),'\n')



# Try to create the file
openfile(FILE_NAME, True)
sleep(1) # Let resource usage drain

# Try to remove it
removefile(FILE_NAME)

# Check the resources
lim, usage, stops = getresources()

# Filewrite should be 4096
if usage["filewrite"] != 4096:
  log("File write should be 4096! Usage: "+str(usage),'\n')

