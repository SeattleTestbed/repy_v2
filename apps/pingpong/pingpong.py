def got_connection(ip, port, socketobj, ch, mainch):
  while True:
    try:
      socketobj.send("hello")
      data = socketobj.recv(5)
      if data != "hello":
        print "Warning, data is '"+data+"'"
    except Exception, e:
      if e[0]==32:
        print "Got a broken pipe"
        exitall()
      raise

    sleep(0.01)
  

if callfunc == 'initialize':
  if len(callargs) == 1:
    print "ponging"
    waitforconn(getmyip(), int(callargs[0]), got_connection)
  
  if len(callargs) == 2:
    print "pinging"
    socketobj = openconn(getmyip(), int(callargs[1]))
    while True:
      try:
        data = socketobj.recv(5)
        if data != "hello":
          print "Warning, data is '"+data+"'"
        socketobj.send("hello")
      except Exception, e:
        if e[0]==32:
          print "Got a broken pipe"
          exitall()
        raise
      sleep(0.01)
    
    
