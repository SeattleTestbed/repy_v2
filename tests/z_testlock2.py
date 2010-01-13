def foo():
  mycontext['lock'].acquire()
  sleep(.5)
  if mycontext['val'] != 0:
    print "ERROR, first 'val' check failed"
    # error, this should be 0...
  mycontext['val'] = 1

  mycontext['lock'].release()
  sleep(.2)

  mycontext['lock'].acquire()
  if mycontext['val'] != 2:
    print "ERROR, third 'val' check failed"

if callfunc=='initialize':
  mycontext['lock'] = getlock()
  mycontext['val'] = 0
  myval = settimer(.0,foo,())

  # wait long enough to let the timer get the lock
  sleep(.2)
  mycontext['lock'].acquire()
  
  if mycontext['val'] != 1:
    # error, this should be 1...
    print "ERROR, second 'val' check failed"
  mycontext['val'] = 2
  # the timer should have the lock and this should never print
  mycontext['lock'].release()

  

