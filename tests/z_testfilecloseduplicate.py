if callfunc == "initialize":
  fobj = open("junk_test.out", "wb")
  fobj.close()
  if fobj.close():
    print "a duplicate fobj.close() should return false"
