"""
This unit test checks the removefile API resource usage.

We check that:
  1) 4K fileread is used on success or failure
  2) 4K filewrite is used on success
"""

FILE_NAME = "removefile.z_testremovefile_resources.py"

try:
  removefile(FILE_NAME)
except FileNotFoundError:
  pass
else:
  print "File: '"+FILE_NAME+"' should not exist!"

lim, usage, stops = getresources()
if usage["fileread"] != 4096:
  print "File read should be 4096! Usage: "+str(usage)



# Try to create the file
openfile(FILE_NAME, True)
sleep(1) # Let resource usage drain

# Try to remove it
removefile(FILE_NAME)

# Check the resources
lim, usage, stops = getresources()

# Filewrite should be 4096
if usage["filewrite"] != 4096:
  print "File write should be 4096! Usage: "+str(usage)

