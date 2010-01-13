# This test tries to do recvmess / stopcomm in a loop

def foo(ip,port,mess, ch):
  print ip,port,mess,ch

if callfunc == 'initialize':
  for x in xrange(0,10):
    ch = recvmess(getmyip(),<messport>,foo)
    sleep(.1)
    stopcomm(ch)
    sleep(.1)
