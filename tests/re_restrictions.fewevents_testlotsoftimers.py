def foo(timername):
  mycontext[timername] = True
  sleep(2)

if callfunc=='initialize':
  mycontext['timetogo'] = False
  myval = settimer(.2, foo, ('a',))
  myval = settimer(.3, foo, ('b',))
  myval = settimer(.4, foo, ('c',))
  sleep(1)
  if mycontext['a'] and mycontext['b'] and mycontext['c']:
    print "Bye!"

  

