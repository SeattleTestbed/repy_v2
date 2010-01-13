def foo(ip,port,mess, ch):
  print ip,port,mess,ch
  stopcomm(ch)

if callfunc == 'initialize':
  ip = getmyip()
  recvmess(ip,<messport>,foo)
  sleep(.1)
  sendmess(ip,<messport>,'hi')
