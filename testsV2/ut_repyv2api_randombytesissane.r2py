"""
This unit test checks the randombytes API call.

We check:
  1) 1024 bytes are returned * 2
  2) No character is repeated more than 20 times.
  3) Every character is there at least 1 time.

"""

#pragma repy

# Get the random data
data = randombytes() + randombytes() + randombytes() + randombytes()

# Check the length
if len(data) != 4096:
  log("Length is incorrect! Is: "+str(len(data)),'\n')

# Initialize the occur count to 0
occur_count = {}
for x in xrange(256):
  occur_count[x] = 0

# Process the string
for char in data:
  val = ord(char)
  occur_count[val] += 1

# Check that everything is equally distributed
for x in xrange(256):
  count = occur_count[x]
  if count < 1:
    log("Character with value '"+str(x)+"' occurs only "+str(count)+" times. Min 1",'\n')
  if count > 40:
     log("Character with value '"+str(x)+"' occurs "+str(count)+" times. Max 20"   ,'\n')

