"""
  We want to test that willblock's behavior is sane.
  Namely prior to any writes, recv() should block and send() should not
"""

# What port should we use?
PORT = <connport>

# Get a lock and initialize it to being locked.
# Once we have connected to the waitforconn, we will release CONNECTED_LOCK
# Once we are done processing, we will release the DONE_LOCK
CONNECTED_LOCK = getlock()
DONE_LOCK = getlock()
if callfunc == "initialize":
  CONNECTED_LOCK.acquire()
  DONE_LOCK.acquire()

# Incoming connection handler
def incoming(ip, port, server_sock, ch1,ch2):
  # Get the client socket
  CONNECTED_LOCK.acquire()
  client_sock = mycontext["client"]

  # Test willblock has sane initial values
  read_will_block, write_will_block = client_sock.willblock()
  if not read_will_block:
    print "Client read should block! We haven't sent any data!"
  if write_will_block:
    print "Client write shouldn't block! We haven't filled the buffer!"

  # Check the server
  read_will_block, write_will_block = server_sock.willblock()
  if not read_will_block:
    print "Server read should block! We haven't sent any data!"
  if write_will_block:
    print "Server write shouldn't block! We haven't filled the buffer!"

  server_sock.close()

  # Done now
  DONE_LOCK.release()
  

def timeout():
  print "Test timed out!"
  exitall()

def main():
  # Setup a timeout
  timeh = settimer(10,timeout,())

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
  canceltimer(timeh)
  stopcomm(waith)
  client_sock.close()


# Call the main function
if callfunc == "initialize":
  main()


