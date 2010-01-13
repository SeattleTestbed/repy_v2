def foo():
  print "Hi"

if callfunc=='initialize':
  
  myval = settimer(3,foo,())
  sleep(.01)
  canceltimer(myval)
  

