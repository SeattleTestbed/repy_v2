def foo():
  exitall()

if callfunc=='initialize':
  settimer(0.1, foo, ())
  sleep(.5)
  print 'OK!'
