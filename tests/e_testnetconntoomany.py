def foo(ip,port,sockobj, ch,mainch):
  
  # just wait when getting a connection
  sleep(.1)

  # this is so a bad test will eventually exit...
  mycontext['count'] = mycontext['count']  + 1
  if mycontext['count'] == 3:
    stopcomm(ch)
    stopcomm(mainch)


if callfunc == 'initialize':
  mycontext['count'] = 0

  ip = getmyip()

  waitforconn(ip,<connport>,foo)
  sleep(.1)
  sockobj  = openconn(ip,<connport>)
  sockobj2 = openconn(ip,<connport>)
  sockobj3 = openconn(ip,<connport>) 
  sockobj4 = openconn(ip,<connport>)
  sockobj5 = openconn(ip,<connport>)
  sockobj6 = openconn(ip,<connport>)# should be an error (too many outsockets)

#  sockobj.close()
