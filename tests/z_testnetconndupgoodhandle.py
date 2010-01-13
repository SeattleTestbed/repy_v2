def foo(ip,port,sockobj, ch,mainch):
  raise Exception, "Should not be here"

def noop(ip, port, sockobj, ch, mainch):
  stopcomm(ch)
  stopcomm(mainch)
  

if callfunc == 'initialize':

  ip = getmyip()

  waitforconn(ip,<connport>,foo)
  ch = waitforconn(ip,<connport>,noop)  # should return a valid handle
  if ch == None:
    raise Exception, "Returned commhandle must not be None!"

  stopcomm(ch)
