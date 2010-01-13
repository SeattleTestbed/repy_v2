
if callfunc == "initialize":
  ip = getmyip()
  port = <connport>
  # Use yahoo.com to avoid a conflict with the duplicateopenconn test
  remoteip = gethostbyname_ex("yahoo.com")[2][1]
  remoteport = 80
  
  # First openconn should work fine
  try:
    sock1 = openconn(remoteip, remoteport, ip, port,timeout=300)
  except Exception, e:
    print "Unexpected exception! '"+str(e)+"' of type '"+str(type(e))+"'."
    exitall()
  
  # This should fail, sock1 is open
  try:
    sock2 = openconn(remoteip, remoteport, ip, port)
  except:
    # This is expected
    pass
  else:
    print "Unexpectedly created a new socket! Reused network tuple!"  
    sock2.close()

  # Close the socket, now re-try. openconn should block until the socket is available
  sock1.close()
  
  # This should block, but we eventually get the socket
  try:
    # Set a sufficiently long timeout that the socket should eventually get cleared
    # The time wait state can take up to 10 minutes, but should not do so normally
    # setting this too short causes failures for our unit tests on some platforms
    sock2 = openconn(remoteip, remoteport, ip, port, timeout=600)
  except Exception, e:
    print "Unexpected exception! '"+str(e)+"' of type '"+str(type(e))+"'.   We should block execution!"
  else:  
    sock2.close()


