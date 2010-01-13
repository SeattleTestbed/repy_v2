if callfunc == "initialize":
  fobj = open("junk_test.out", 'w')
  fobj.writelines(["hello"])
  fobj.close()

  fobj = open("junk_test.out", 'r')
  contents = fobj.read()
  if not contents == "hello":
    print "This shouldn't happen! Read '%s' instead of 'hello'." % contents

  fobj.close()
