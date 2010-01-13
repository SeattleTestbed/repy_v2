def foo(ip,port,mess, ch):
  print ip,port,mess,ch

if callfunc == 'initialize':
  ch = recvmess(getmyip(),<messport>,foo)
  sleep(.1)
  stopcomm(ch)
