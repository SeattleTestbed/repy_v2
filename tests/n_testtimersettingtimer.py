def foo():
  mycontext['foo'] = mycontext['foo'] + 1
  if mycontext['foo'] < 5:
    settimer(0.1, foo, ())
    return
  print "Bye"


if callfunc=='initialize':
  mycontext['foo'] = 0
  settimer(0.1, foo, ())
