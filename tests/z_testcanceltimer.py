def foo():
  print 'OK!'

if callfunc=='initialize':
  timerval = settimer(5, foo, ())
  canceltimer(timerval)
  

