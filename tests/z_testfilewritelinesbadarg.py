if callfunc == "initialize":
  fobj = open("junk_test.out", 'w')
  try:
    fobj.writelines(5)
  # This will be a namespace.NamespaceViolationError
  except Exception:
    pass
  else:
    print "This shouldn't happen!"
  finally:
    fobj.close()
