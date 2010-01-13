def foo(a,b,c,d):
  print a,b,c,d

if callfunc=='initialize':
  settimer(0.1, foo, ('hi',7,None,3.2))
