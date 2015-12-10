"""
This test checks the behavior of openfile when filehandles should be exhausted.
"""

#pragma repy
filehandles = []
filenames = []

RAND_FILE = "random.files.to.create.number"

# Open random files, as many as the resource restrictions allows  
for number in xrange(getresources()[0]['filesopened']):
  filenames.append(RAND_FILE + str(number + 1))
  filehandles.append(openfile((RAND_FILE + str(number + 1)), True))

# Try to open this file with create, we should get an error
# and the file should not be created
TRYFILE = "trying.to.create.this.file"

try:
  fileh = openfile(TRYFILE, True)
except ResourceExhaustedError:
  pass
else:
  log("Opened file with no handles available!",'\n')
# Check if the file exists
if TRYFILE in listfiles():
  log("The file was created with no handles available!",'\n')
  fileh.close()
  removefile(TRYFILE)

#Close all random files opened
for randfile in filehandles:
  randfile.close()

#Clean up all random files
for name in filenames:
  removefile(name)