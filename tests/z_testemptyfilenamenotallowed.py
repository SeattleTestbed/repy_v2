if callfunc == "initialize":
  try:
    f = open("")
  except TypeError:
    pass
  else:
    print "open() on the empty string should raise TypeError"
