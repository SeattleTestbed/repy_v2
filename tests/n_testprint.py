def foo():
  raise Exception, "timed out!"

if callfunc=='initialize':
  settimer(1.0, foo, ())
  print "hello, this a lot to print"
  exitall()
