# This test checks that the cleanup stopcomm does is complete
# We should not be able to do an openconn after stopcomm finishes

def noop(ip,port,sock,ch1,ch2):
  pass


if callfunc == "initialize":
  ip = getmyip()
  port = <connport>
  count = 0
  while count < 8:
    count += 1
    waith = waitforconn(ip,port,noop)
    stopcomm(waith)
    try:
      sock = openconn(ip,port,timeout=2)
    except:
      pass
    else:
      print "Able to connect!"
      sock.close()
      break


