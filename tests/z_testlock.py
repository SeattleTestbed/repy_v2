def foo():
  mycontext['lock'].acquire()
  sleep(.5)
  exitall()

if callfunc=='initialize':
  mycontext['lock'] = getlock()
  myval = settimer(.0,foo,())

  # wait long enough to let the timer get the lock
  sleep(.2)
  mycontext['lock'].acquire()
  # the timer should have the lock and this should never print
  print "Should not get here"

  

