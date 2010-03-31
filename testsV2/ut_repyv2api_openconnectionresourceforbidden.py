"""
Check that connecting from a bad port will result in an ResourceForbiddenError
"""
#pragma repy

localip = "127.0.0.1"
localport = 34232  # bad port
remoteip = "127.0.0.1"
remoteport = 43214
timeout = 1.0

try:
  # Even though I'm connecting to something invalid, the ResourceForbiddenError
  # has precedence
  openconnection(remoteip, remoteport, localip,localport, timeout)
except ResourceForbiddenError:
  pass
else:
  log("Did not get ResourceForbiddenError using a disallowed port",'\n')


