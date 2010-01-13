def foo():
  mycontext['timetogo'] = True

if callfunc=='initialize':
  mycontext['timetogo'] = False
  myval = settimer(.1,foo,())
  sleep(1)
  if mycontext['timetogo']:
    print "Bye!"

  

