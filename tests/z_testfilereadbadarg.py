if callfunc == "initialize":
  # Make sure the file exists.
  open("junk_test.out", 'w').close()
  
  fobj = open("junk_test.out", 'rb')
  try:
    for arg in [3.0, "hi"]:
      try:
        fobj.read(arg)
      except Exception, e:
        if "TypeError" in str(type(e)):
          pass
        else:
          raise Exception("fobj.read() should raise TypeError when given a bad len argument")
  finally:
    fobj.close()
