# This test only has many iface flags with common interfaces to try to get one
# with a real IP that we are allowed to bind to it

def noop(ip,port,mess,ch):
  sleep(30)

if callfunc == 'initialize':
  ip = getmyip()
  if ip == "127.0.0.1":
    print "Got unexpected IP:"+ip+" Expected real IP address!"
  
  recvmess(ip,12345,noop)
  sleep(1)
  exitall()
