"""
This test checks that a successful listenforconnection
consumes an insocket.
"""
#pragma repy

ip = "127.0.0.1"
port = 12345

lim, usage, stops = getresources()
if usage["insockets"] != 0:
  print "Initial insockets should be 0!"

listen_sock = listenforconnection(ip, port)

lim, usage, stops = getresources()
if usage["insockets"] != 1:
  print "After insockets should be 1!"

listen_sock.close() # Stop

lim, usage, stops = getresources()
if usage["insockets"] != 0:
  print "Post insockets should be 0!"

