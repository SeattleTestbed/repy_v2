def bar(ip,port,mess, ch):
  
  # just wait when getting a connection
  sleep(.1)


def foo(ip,port,sockobj, ch,mainch):
  
  # just wait when getting a connection
  sleep(.1)


if callfunc == 'initialize':
  mycontext['count'] = 0

  ip = getmyip()

  ch1 = waitforconn(ip,<connport>,foo)
  ch2 = recvmess(ip,<messport1>,bar)
  ch3 = waitforconn(ip,<connport2>,foo) # should be an error, insockets > 2
  sleep(.1)
  stopcomm(ch1)
  stopcomm(ch2)
  stopcomm(ch3)

#  sockobj.close()
