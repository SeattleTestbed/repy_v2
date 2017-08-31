"""
Check that closing a server socket doesn't impact connected sockets
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


# Okay, I no longer need the server socket
tcpserversocket.close()


# now let's test the client socket...

# shouldn't be able to buffer more than thins
MAXSENDSIZE = 1024*1024

# send until it would block
totalamountsent = 0
while True:
  try:
    amountsent = conn.send('h'*(MAXSENDSIZE-totalamountsent))
  except SocketWouldBlockError:
    # This should happen at some point.
    break
  
  assert(amountsent > 0)

  totalamountsent = totalamountsent + amountsent

  assert(MAXSENDSIZE != totalamountsent)


totalamountrecvd = 0

while totalamountrecvd < totalamountsent:
  
  # now the server should be able to recv that amount of data...
  data = serverconn.recv(totalamountsent-totalamountrecvd)

  totalamountrecvd = totalamountrecvd + len(data)


assert totalamountrecvd == totalamountsent


# but no more
try: 
  serverconn.recv(1)
except SocketWouldBlockError:
  pass
else:
  log("Should not be able to recv more than was sent...",'\n')


conn.close()
serverconn.close()
