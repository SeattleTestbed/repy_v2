"""
Check that open after listen is forbidden.
"""
#pragma repy

localip = "127.0.0.1"
localport = 12345
remoteip = "127.0.0.1"
remoteport = 43214
timeout = 1.0

tcpserversocket = listenforconnection(localip, localport)

try:
  # Even though I'm connecting to something invalid, the AlreadyListeningError
  # has precedence
  openconnection(remoteip, remoteport, localip,localport, timeout)
except AlreadyListeningError:
  pass
else:
  log("Did not get AlreadyListeningError when connecting after a listen",'\n')

tcpserversocket.close()
