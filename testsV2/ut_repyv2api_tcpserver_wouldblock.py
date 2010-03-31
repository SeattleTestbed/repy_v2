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
  log("Did not get an exception! Got: "+str(info),'\n')
except SocketWouldBlockError:
  pass

listen_sock.close() # Stop


