if callfunc == "initialize":
  # first, initialize by creating the file we'll read.
  fobj = open("junk_test.out", 'w')
  fobj.write("hello\n")
  fobj.close()
  
  # now the actual test
  fobj = open("junk_test.out", 'rb')
  line = fobj.readline(3)
  if len(line) > 3:
    print "This shouldn't happen!"
