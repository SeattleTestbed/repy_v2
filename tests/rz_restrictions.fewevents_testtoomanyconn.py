def foo(ip,port,sockobj, ch,mainch):
  
  mycontext['count'] = mycontext['count']  + 1
 
  if mycontext['count'] > 2:
    print "Should have exited before this connection was accepted"

  # just wait when getting a connection
  sleep(.5)

  # this is so a bad test will eventually exit...
  if mycontext['count'] == 3:
    stopcomm(ch)
    stopcomm(mainch)


if callfunc == 'initialize':
  mycontext['count'] = 0

  ip = getmyip()

  ch1 = waitforconn(ip,<connport>,foo)
  junk1 = openconn(ip,<connport>)
  junk2 = openconn(ip,<connport>)
  junk3 = openconn(ip,<connport>) # should never be connected
  sleep(.1)
  stopcomm(ch1)

#  sockobj.close()
