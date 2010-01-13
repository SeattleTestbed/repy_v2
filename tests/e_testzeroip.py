def foo(ip,port,mess, ch):
  print ip,port,mess,ch

if callfunc == 'initialize':
  # a null IP is not allowed
  ch = recvmess('0.0.0.0',<messport>,foo)
  sleep(.1)
  stopcomm(ch)
