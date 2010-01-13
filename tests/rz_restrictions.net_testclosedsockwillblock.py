
# Make sure recv() and willblock() raise "Socket closed" after calling sock.close()

# Listen port
PORT = <connport>

# Get a lock and initialize it to being locked.
# Once we have connected to the waitforconn, we will release CONNECTED_LOCK
# Once we are done processing, we will release the DONE_LOCK
CONNECTED_LOCK = getlock()
DONE_LOCK = getlock()
if callfunc == "initialize":
  CONNECTED_LOCK.acquire()
  DONE_LOCK.acquire()


# Helper to close sockets
def closeit(sock):
  sock.close()

# Helper to check what recv() throws while its doing select()
def check_recv(sock):
  try:
    data = sock.recv(16)
  except Exception, e:
    if str(e) != "Socket closed":
      print "Got bad exception! recv() should throw 'Socket closed' got: " + str(e)

# Helper to check what willblock() throws when the socket gets closed
def check_willblock(sock):
  try:
    while True:
      (r,w) = sock.willblock()
      sleep(0.04)
  except Exception, e:
    if str(e) != "Socket closed":
      print "Got bad exception! willblock() should throw 'Socket closed' got: " + str(e)


# Incoming connection handler
def incoming(ip, port, server_sock, ch1,ch2):
  # Get the client socket
  CONNECTED_LOCK.acquire()
  client_sock = mycontext["client"]

  # Start two threads to check recv()
  settimer(0,check_recv,[client_sock])
  settimer(0,check_recv,[server_sock])

  # Start two threads to check willblock()
  settimer(0, check_willblock, [client_sock])
  settimer(0, check_willblock, [server_sock])

  # Now close both sockets
  settimer(0.2, closeit, [client_sock])
  settimer(0.2, closeit, [server_sock])

  # Wait for it...
  sleep(0.3)

  # Done now
  DONE_LOCK.release()
  

def main():
  # Get our ip
  ip = getmyip()

  # Setup a waitforconn
  waith = waitforconn(ip, PORT, incoming)

  # Get the client socket
  client_sock = openconn(ip, PORT)

  # Share the client socket and enable
  mycontext["client"] = client_sock

  # Wait until we are done
  CONNECTED_LOCK.release()
  DONE_LOCK.acquire()

  # Cleanup
  stopcomm(waith)


# Call the main function
if callfunc == "initialize":
  main()

