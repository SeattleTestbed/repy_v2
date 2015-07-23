"""
This test checks the behavior of openfile when filehandles should be exhausted.
"""

#pragma repy
filehandles = []


RAND_FILE = "random.files.to.create.number"

# Open random files
for x in xrange(getresources()[0]['filesopened']):
  filehandles.append(openfile((RAND_FILE + str(x + 1)), True)) # the plus 1 is for getting to 250 files!

# Try to open this file with create, we should get an error
# and the file should not be created
TRY_FILE = "trying.to.create.this.file"

try:
  fileh = openfile(TRY_FILE, True)
except ResourceExhaustedError:
  pass
else:
  log("Opened file with no handles available!",'\n')

# Check if the file exists
if TRY_FILE in listfiles():
  log("The file was created with no handles available!",'\n')
