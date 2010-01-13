"""
  We want to test that willblock's behavior is sane.
  Namely if we write, then recv() should not block
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

  # Lets get some large amount of random data to exhaust the buffers
  data = "Random data. This is junk."
  data = data * 45000

  # Lets try to send all this to the client
  server_sent = server_sock.send(data)

  # Make sure we sent something...
  if server_sent == 0:
    print "Failed to send any data with an empty buffer!"
  elif server_sent < 4096:
    print "Only send 1 page of data! This seems too low for an empty buffer."
  elif server_sent == len(data):
    print "Sent all the data! This should have been more than the buffer!"

  # Wait to make sure the data arrives, reduces flaky failures
  sleep(0.1)

  # The client's read should NOT block now
  read_will_block, write_will_block = client_sock.willblock()
  if read_will_block:
    print "Client read should not block! There should be available data!"
  
  
  # Now, we will read 4096 bytes from the client, and this should unblock the server's send
  client_read = client_sock.recv(4096)

  # The client's read should still not block, there should be more data
  read_will_block, write_will_block = client_sock.willblock()
  if read_will_block:
    print "Client read (2) should not block! There should be more available data!"

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


