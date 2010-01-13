try:
  
  try:
    raise Exception, "Exiting"
  finally:
    print "Hi"  # should be printed
except Exception:
  pass
