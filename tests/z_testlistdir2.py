
# create the file if it doesn't exist...
try:
  fro = open("junk_test.out","w")
  fro.close()
except:
  pass

filelistbefore = listdir()
removefile("junk_test.out")
filelistafter = listdir()

if "junk_test.out" not in filelistbefore:
  print "OOPS! Created files don't show up in file list..."

if "junk_test.out" in filelistafter:
  print "OOPS! Removed files don't disappear from file list..."
  

