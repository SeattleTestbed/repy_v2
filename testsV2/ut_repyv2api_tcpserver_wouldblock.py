"""
This test checks that a listening TCP socket throws
a SocketWouldBlockError if there are no connections waiting.
"""
#pragma repy

ip = "127.0.0.1"
port = 12345

listen_sock = listenforconnection(ip, port)
try:
  info = listen_sock.getconnection()
  print "Did not get an exception! Got: "+str(info)
except SocketWouldBlockError:
  pass

listen_sock.close() # Stop


