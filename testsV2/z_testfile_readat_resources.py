"""
This checks the resource accounting of file.readat()
"""

# Get a filehandle
fileh = openfile("repy.py", False)
sleep(.25) # Flush the usage

# Read 1 byte, we should get charged for 4096
fileh.readat(1,0)

# Check the usage
lim, usage, stops = getresources()
if usage["fileread"] != 4096:
  print "We should be charged for an entire block! Usage: "+str(usage)

# Wait to flush
sleep(.25)

# Try a non-aligned read, get charged for 2 blocks
fileh.readat(8, 4090)

# Check the usage
lim, usage, stops = getresources()
if usage["fileread"] != 4096*2:
  print "We should be charged for 2 entire blocks! Usage: "+str(usage)

# Done
fileh.close()

