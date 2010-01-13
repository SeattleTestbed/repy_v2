"""
  We want to test that willblock's behavior is sane.
  If we recv() from a full buffer, we should unblock send() for our partner.
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

  # Lets try to send all this to the client, loop until we would block
  wblock = False
  sent = 1
  total_sent = 0
  while not wblock and sent > 0:
    sent = server_sock.send(data)
    total_sent += sent
    sleep(0.04)
    rblock,wblock = server_sock.willblock()


  # Now, we will keep reading 4096 bytes from the client until this unblocks the server's send
  client_rblocks = False
  server_wblocks = True
  total_read = 0
  while not client_rblocks and server_wblocks:
    client_read = client_sock.recv(4096)
    total_read += len(client_read)
    client_sock.send("read") # Sending some data should force us to ACK the received data
    sleep(0.04)
    client_rblocks,junk = client_sock.willblock()
    junk,server_wblocks = server_sock.willblock()

  # Check that we read less than we sent
  if not total_read < total_sent:
      print "We shouldn't need to read everything that was sent to unblock send!"

  # Check the server socket now
  rblock,wblock = server_sock.willblock() 
  if wblock:
    print "Write should not block since the client has read some data!"
  
  # Try to send again from the server
  server_sent_2 = server_sock.send(data)

  if server_sent_2 == 0:
    print "Failed to send any data with a mostly full buffer! Should be room though."
  elif server_sent_2 < 4096:
    print "Was able to send less than 4096 bytes. Sent: " + str(server_sent_2)

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


