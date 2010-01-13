def foo():
  mycontext['timetogo'] = True
  while mycontext['foogo'] == False:
    pass

if callfunc=='initialize':
  mycontext['timetogo'] = False
  mycontext['foogo'] = False
  myval = settimer(.1,foo,())
  mycontext['foogo'] = True

if callfunc=='exit':
  if mycontext['timetogo']:
    print "Bye!"
  

