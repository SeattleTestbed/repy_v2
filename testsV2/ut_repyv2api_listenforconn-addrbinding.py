"""
This unit test checks that we get a AddressBindingError
when providing bad IP's to listenforconnection.
"""
#pragma repy

PORT = 12345

def tryit(ip):
  try:
    listenforconnection(ip,PORT)
    log("Bad combination worked! IP:"+str(ip)+" Port: "+str(port),'\n')
  except AddressBindingError:
    pass

# Try some bad combos
tryit("72.123.45.62")
tryit("12.10.3.1")
tryit("123.214.111.221")


