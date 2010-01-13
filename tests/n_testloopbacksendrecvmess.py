def foo(ip,port,mess, ch):
  print ip,port,mess,ch
  stopcomm(ch)

if callfunc == 'initialize':
  recvmess('127.0.0.1',<messport>,foo)
  sleep(.1)
  sendmess('127.0.0.1',<messport>,'hi')
