
if callfunc == "initialize":
  ip = getmyip()
  port = <connport>
  remoteip = gethostbyname_ex("google.com")[2][-1]
  remoteport = 80
  
  # First openconn should work fine
  try:
    sock1 = openconn(remoteip, remoteport, ip, port)
  except Exception, e:
    print "Unexpected Exception! '"+str(e)+"'"
    exitall()
  
  # This should fail, sock1 is open
  try:
    sock2 = openconn(remoteip, remoteport, ip, port)
  except Exception,e:
    if "Duplicate" in str(e):
      pass
    else:
      print "Expected error about duplicate handles! Got:"+str(e)
  else:
    print "Unexpectedly created a new socket! Reused network tuple!"  
    sock2.close()


