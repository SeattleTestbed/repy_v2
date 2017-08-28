"""
Check that socket.send will raise a SocketWouldBlockError after we
have tried to exhaust the socket buffer up to a sane maximum (which
needs some fine-tuning). We test this on a connection on localhost.
"""
#pragma repy restrictions.twoports

localip = "127.0.0.1"
localport = 12345
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0

# We assume this to be an okay socket buffer size. If the buffer is
# larger than this, the unit test fails!
SANE_MAX_BUFFER_SIZE = 1024 * 1024

tcpserversocket = listenforconnection(targetip, targetport)

conn = openconnection(targetip, targetport, localip, localport, timeout)


(ip, port, serverconn) = tcpserversocket.getconnection()

assert(ip == localip)
assert(port == localport)



# Keep sending until the socket would block (OK, no problem) or the
# buffer is more than exhausted (BAD).
totalamountsent = 0
while True:
  try:
    amountsent = conn.send('h'*SANE_MAX_BUFFER_SIZE)
  except SocketWouldBlockError:
    # This should happen at some point.
    break
  totalamountsent = totalamountsent + amountsent
  if totalamountsent > SANE_MAX_BUFFER_SIZE:
    log("The socket buffered more than", SANE_MAX_BUFFER_SIZE, "bytes.\n")
    break


# The server should be able to receive that amount of data...
totalamountrecvd = 0

while totalamountrecvd < totalamountsent:
  data = serverconn.recv(totalamountsent-totalamountrecvd)
  totalamountrecvd = totalamountrecvd + len(data)

if totalamountrecvd != totalamountsent:
  log("Received more than the", totalamountsent, "bytes sent previously!\n")

# ...but no more
try: 
  serverconn.recv(1)
except SocketWouldBlockError:
  pass
else:
  log("Receive buffer should be empty but did not block on recv!\n")

tcpserversocket.close()

