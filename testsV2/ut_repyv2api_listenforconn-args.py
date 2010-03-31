"""
This unit test checks that we get a RepyArgumentError
when providing bad arguments to listenforconnection.
"""
#pragma repy

def tryit(ip,port):
  try:
    listenforconnection(ip,port)
    log("Bad combination worked! IP:"+str(ip)+" Port: "+str(port),'\n')
  except:
    pass

# Try some bad combos
tryit(None, None)
tryit("abcd", 12345)
tryit("0.0.0.0", 12345)
tryit("255.255.255.255", 12345)
tryit("192.168.0.0", 12345)

tryit("127.0.0.1", 0)
tryit("127.0.0.1", 3.1415)
tryit("127.0.0.1", -2)

