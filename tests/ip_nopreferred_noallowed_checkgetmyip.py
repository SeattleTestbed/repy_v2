# This test only has the
# --iface lo flag, and we want to be sure getmyip returns an IP that is loopback
# and that we are allowed to bind to it

def noop(ip,port,mess,ch):
  sleep(30)

if callfunc == 'initialize':
  ip = getmyip()
  if ip != "127.0.0.1":
    print "Got unexpected IP:"+ip+" Expected loopback IP address!"
  
  recvmess(ip,12345,noop)
  sleep(1)
  exitall()
