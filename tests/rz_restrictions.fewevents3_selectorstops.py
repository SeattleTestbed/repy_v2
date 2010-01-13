# a test to see if the event used by the socket selector is reclaimed...
def foo(ip,port,sockobj, ch,mainch):
  
  # just wait when getting a connection
  sleep(.1)


def bar():
  print "bar"

def noop():
  pass

def baz():
  print "baz"

if callfunc == 'initialize':
  mycontext['count'] = 0

  ip = getmyip()

  ch1 = waitforconn(ip,<connport>,foo)
  junk = openconn(ip,<connport>) 
  stopcomm(ch1)
  junk.close()
  sleep(.5)   # it should be cleaned up now
  settimer(5, noop,())
  settimer(.2, exitall,())
  # execute further in the future than this should take
  # try until this executes...
  while True:
    try:
      settimer(.0, baz,())
      break
    except:
      pass
  


#  sockobj.close()
