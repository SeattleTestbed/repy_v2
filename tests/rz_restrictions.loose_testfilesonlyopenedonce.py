# This tests that files are only allowed to be open once, and raise the
# correct exception.

if callfunc == 'initialize':
  a = open("a.file", "wb")
  try:
    b = open("a.file", "wb")
    print "This shouldn't get printed."
    b.close()
  except ValueError:
    pass
  finally:
    a.close()
