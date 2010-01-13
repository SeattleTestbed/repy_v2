def foo(ip,port,sockobj, ch,mainch):
  raise Exception, "Should not be here"

def noop(ip, port, sockobj, ch, mainch):
  stopcomm(ch)
  stopcomm(mainch)
  

if callfunc == 'initialize':

  ip = getmyip()

  waitforconn(ip,<connport>,foo)
  waitforconn(ip,<connport>,noop)  # should overwrite foo...
  sleep(.1)
  sockobj = openconn(ip,<connport>)

  sockobj.close()
