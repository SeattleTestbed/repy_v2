"""
Check that connecting where there isn't a listener will give the appropriate
exception
"""
#pragma repy

localip = "127.0.0.1"
localport = 12345
remoteip = "127.0.0.1"
remoteport = 43214
timeout = 1.0

try:
  openconnection(remoteip, remoteport, localip,localport, timeout)
except ConnectionRefusedError:
  pass
else:
  log("Did not get ConnectionRefusedError connecting to a non-existent listener.",'\n')


