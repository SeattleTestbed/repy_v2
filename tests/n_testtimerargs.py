def foo(outdata):
  print outdata

if callfunc=='initialize':
  settimer(0.1, foo, ("Hello!",))
