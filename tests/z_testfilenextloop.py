if callfunc == "initialize":
  # Make sure the file exists.
  open("junk_test.out", 'w').close()
  
  fobj = open("junk_test.out")
  for line in fobj:
    pass

  try:
    fobj.next()
  except StopIteration:
    pass
  else:
    raise Exception('Should raise StopIteration')
  finally:
    fobj.close()
