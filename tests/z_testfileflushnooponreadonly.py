if callfunc == "initialize":
  # first, create the file, we'll read...
  fobj = open("junk_test.out","w")
  fobj.close()

  # Now the actual test...
  try:
    fobj = open("junk_test.out", 'r')
    fobj.flush()
    # flush on a read-only file should be a no-op
  finally:
    fobj.close()
