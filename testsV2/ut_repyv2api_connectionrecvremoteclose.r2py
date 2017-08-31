"""
Check what happens when trying to recv from a socket that was closed on the remote end.
"""
#pragma repy restrictions.twoports

localip = "127.0.0.1"
localport = 12345
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0


tcpserversocket = listenforconnection(targetip, targetport)

conn = openconnection(targetip, targetport, localip, localport, timeout)


(ip, port, serverconn) = tcpserversocket.getconnection()

assert(ip == localip)
assert(port == localport)

serverconn.close()
try:
  data = conn.recv(10)
except SocketClosedRemote:
  pass
else:
  log("Should get an error that the other side closed the socket",'\n')

