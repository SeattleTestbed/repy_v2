"""
This test checks the behavior of openfile when filehandles should be exhausted.
"""

#pragma repy

MAX_FILES = 5

files = listfiles()
filehandles = [None, None, None, None, None]

# Open random files
for x in xrange(MAX_FILES):
  filehandles[x] = openfile(files[x], False)

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

