def foo():
  a = [1] * 2**21
  mycontext['lock'].acquire()
  mycontext['count'] = mycontext['count'] + 1
  mycontext['lock'].release()
  while True:
    sleep(.001)
    if mycontext['count'] == 5:
      sleep(5)
      print "Failed, exiting"
      exitall()

if callfunc=='initialize':
  mycontext['lock'] = getlock()
  mycontext['count'] = 0
  settimer(0,foo,())
  settimer(.2,foo,())
  settimer(.4,foo,()) # I think this should come close, to the mem limit...
  settimer(.6,foo,())
  settimer(.8,foo,())

  
