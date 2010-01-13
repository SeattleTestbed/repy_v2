# More than two events are not allowed:

def bar():
  while True: pass

def foo():
  settimer(0,bar,[])
  settimer(0,bar,[])
  
if callfunc == 'initialize':
  settimer(1,foo,[])
