# This test only has the
# --ip 127.0.0.1 flag, and we want to be sure getmyip returns 127.0.0.1,
# and that we are allowed to bind to it

def noop(ip,port,mess,ch):
  sleep(30)

if callfunc == 'initialize':
  ip = getmyip()
  if ip != "127.0.0.1":
    print "Got unexpected IP:"+ip+" Expected: 127.0.0.1"
  
  recvmess('127.0.0.1',12345,noop)
  sleep(2)
  exitall()
