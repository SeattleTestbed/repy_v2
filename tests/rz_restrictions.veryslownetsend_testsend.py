def foo(ip,port,mess, ch):
  stopcomm(ch)
  exitall()

if callfunc == 'initialize':
  ip = getmyip()
  recvmess(ip,<messport>,foo)
  sleep(.1)
  sendmess(ip,<messport>,'hi')
  sendmess(ip,<messport>,'Hello, this is too long of a message to be received in such a short time')
  print "hi"
