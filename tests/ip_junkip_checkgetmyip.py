# This test only has the
# --ip 256.256.256.256 flag, and we want to be sure getmyip doesn't returns this IP
# we should get the loopback IP

def noop(ip,port,mess,ch):
  sleep(30)

if callfunc == 'initialize':
  ip = getmyip()
  if ip != "127.0.0.1":
    print "Got unexpected IP:"+ip+" Expected: 127.0.0.1!"
      
  recvmess(ip,12345,noop)
  sleep(1)
  exitall()
