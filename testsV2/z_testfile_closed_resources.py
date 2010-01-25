"""
Checks that file.close() releases a file handle
"""

# Open a filehandle
fileh = openfile("repy.py", False)

# Usage should be 1
lim, usage, stops = getresources()
if usage["filesopened"] != 1:
  print "Only one file should be opened! Usage: "+str(usage)

# Close the handle
fileh.close()

# Usage should be 0
lim, usage, stops = getresources()
if usage["filesopened"] != 0:
  print "No files should be opened! Usage: "+str(usage)


