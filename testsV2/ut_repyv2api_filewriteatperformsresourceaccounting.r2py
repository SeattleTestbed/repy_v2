"""
This checks the resource accounting of file.writeat()
"""

#pragma repy

# Get a filehandle
JUNK_FILE = "this.is.a.junk.file.2340v234"
fileh = openfile(JUNK_FILE, True)
sleep(.25) # Flush the usage

# Write 1 byte, we should get charged for 4096
fileh.writeat("X",0)

# Check the usage
lim, usage, stops = getresources()
if usage["filewrite"] != 4096:
  log("We should be charged for an entire block! Usage: "+str(usage),'\n')

# Wait to flush
sleep(.25)

# Try a non-aligned write, get charged for 2 blocks
fileh.writeat("N"*4098, 1)

# Check the usage
lim, usage, stops = getresources()
if usage["filewrite"] != 4096*2:
  log("We should be charged for 2 entire blocks! Usage: "+str(usage),'\n')

# Done
fileh.close()

# Remove the file
removefile(JUNK_FILE)

