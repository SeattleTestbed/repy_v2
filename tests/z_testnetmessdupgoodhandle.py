def foo(ip,port,sockobj, ch):
  raise Exception, "Should not be here"

def noop(ip, port, sockobj, ch):
  stopcomm(ch)
  

if callfunc == 'initialize':

  ip = getmyip()

  recvmess(ip,<messport>,foo)
  ch = recvmess(ip,<messport>,noop)  # should return a valid handle
  if ch == None:
    raise Exception, "Returned commhandle must not be None!"

  stopcomm(ch)
