def foo(ip,port,mess, ch):
  raise Exception, "Should not get here"

def noop(ip,port,mess, ch):
  stopcomm(ch)

if callfunc == 'initialize':
  ip = getmyip()
  recvmess(ip,<messport>,foo)
  recvmess(ip,<messport>,noop)   # should replace foo
  sleep(.1)
  sendmess(ip,<messport>,'hi')
