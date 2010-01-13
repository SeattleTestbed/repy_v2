# This test only has the
# --ip 256.256.256.256 flag, and we want try to bind to something random "128.0.1.5"  to be sure waitforconn and recvmess fail

def noop(ip,port,mess,ch):
  sleep(30)
  
def noop1(ip,port,mess,ch1, ch2):
  sleep(30)

junkip = "128.0.1.5"

if callfunc == 'initialize':
  try:
    waitforconn("128.0.1.5", 12345, noop1)
  except:
    pass # This is expected
  else:
    print "Error! waitforconn should have failed!"
  
  try:
    recvmess("128.0.1.5", 12345, noop)
  except:
    pass # This is expected
  else:
    print "Error! recvmess should have failed!"
