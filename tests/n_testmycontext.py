def foo():
  mycontext['timetogo'] = True

if callfunc=='initialize':
  mycontext['timetogo'] = False
  myval = settimer(.1,foo,())

if callfunc=='exit':
  if mycontext['timetogo']:
    print "Bye!"
  

