def foo(ip,port,mess, ch):
  print ip,port,mess,ch
  stopcomm(ch)

def noop(a,b,c,d):
  pass

if callfunc == 'initialize':
  ip = getmyip()
  noopch = recvmess(ip,<messport>,noop)
  recvmess(ip,<messport1>,foo)
  sleep(.1)
  sendmess(ip,<messport1>,'hi',ip,<messport>)
  stopcomm(noopch)
