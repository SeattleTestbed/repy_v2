"""
This unit test checks that we get a AlreadyListeningError if you
try to listen on an IP/Port pair that is already in use.
"""
#pragma repy

ip = "127.0.0.1"
port = 12345

listen_sock = listenforconnection(ip, port)

try:
  listen_sock_2 = listenforconnection(ip, port)
  log("Should get AlreadyListeningError!",'\n')
except AlreadyListeningError:
  pass

