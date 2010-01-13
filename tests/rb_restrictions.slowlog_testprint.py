def foo():
  raise Exception, "timed out!"

if callfunc=='initialize':
  settimer(0.1, foo, ())
  print "hello, this a lot to print in such a short time and even a slow timer should fire. But just in case, let's make this super long since some machines *cough*testbed-fbsd*cough* are slow enough that we need to leave a large margin."
  exitall()
