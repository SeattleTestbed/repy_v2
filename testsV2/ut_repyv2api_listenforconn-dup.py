"""
This unit test checks that we get a PortInUseError if you
try to listen on an IP/Port pair that is already in use.
"""
#pragma repy

ip = "127.0.0.1"
port = 12345

listen_sock = listenforconnection(ip, port)

try:
  listen_sock_2 = listenforconnection(ip, port)
  print "Should get PortInUseError!"
except PortInUseError:
  pass

