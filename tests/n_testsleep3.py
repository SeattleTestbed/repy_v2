def foo():
  print "Hi"

if callfunc=='initialize':
  
  myval = settimer(.1,foo,())
  sleep(.5)
  canceltimer(myval)
  

