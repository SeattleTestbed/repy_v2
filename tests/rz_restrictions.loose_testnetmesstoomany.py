def foo(ip,port,mess, ch):
  
  # just wait when getting a connection
  sleep(.1)


if callfunc == 'initialize':
  mycontext['count'] = 0

  ip = getmyip()

  ch1 = recvmess(ip,<messport>,foo)
  ch2 = recvmess(ip,<messport1>,foo)
  ch3 = recvmess(ip,<messport2>,foo) # should be an error because insockets > 2
  sleep(.1)
  stopcomm(ch1)
  stopcomm(ch2)
  stopcomm(ch3)

#  sockobj.close()
