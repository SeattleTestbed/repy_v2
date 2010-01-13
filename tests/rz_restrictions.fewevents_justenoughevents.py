# More than two events are not allowed:

# This tests that two (of two allowed) events can be consumed after
# the 'initialize' event ends (that is, it ending should free up an
# event).

def bar():
  sleep(0.5)

def foo():
  settimer(0,bar,[])
  sleep(0.1)
  
if callfunc == 'initialize':
  settimer(1,foo,[])
