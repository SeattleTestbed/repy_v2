"""
Check that a recv would block in different situations...
"""
#pragma repy restrictions.twoports

localip = "127.0.0.1"
localport = 12345
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0

tcpserversocket = listenforconnection(targetip, targetport)

conn = openconnection(targetip, targetport, localip, localport, timeout)

try:
  # This should raise an exception because it would block...
  conn.recv(10)
except SocketWouldBlockError:
  pass
else:
  log("Did not get a SocketWould Block when reading a fresh client socket",'\n')


(ip, port, serverconn) = tcpserversocket.getconnection()

assert(ip == localip)
assert(port == localport)



try:
  # This should still raise an exception...
  conn.recv(10)
except SocketWouldBlockError:
  pass
else:
  log("Did not get a SocketWould Block when reading a connected client socket",'\n')



try:
  # This should still raise an exception...
  serverconn.recv(10)
except SocketWouldBlockError:
  pass
else:
  log("Did not get a SocketWould Block when reading a server socket",'\n')


