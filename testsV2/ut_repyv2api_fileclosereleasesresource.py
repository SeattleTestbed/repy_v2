"""
Checks that file.close() releases a file handle
"""

#pragma repy

# Open a filehandle
fileh = openfile("repy.py", False)

# Usage should be 1
lim, usage, stops = getresources()
if usage["filesopened"] != 1:
  log("Only one file should be opened! Usage: "+str(usage),'\n')

# Close the handle
fileh.close()

# Usage should be 0
lim, usage, stops = getresources()
if usage["filesopened"] != 0:
  log("No files should be opened! Usage: "+str(usage),'\n')


