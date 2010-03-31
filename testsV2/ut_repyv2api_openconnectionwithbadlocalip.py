"""
Check that connecting from a non-local IP will result in an AddressBindingError
"""
#pragma repy

localip = "1.2.3.4"
localport = 12345
remoteip = "127.0.0.1"
remoteport = 43214
timeout = 1.0

try:
  # Even though I'm connecting to something invalid, the AddressBindingError
  # has precedence
  openconnection(remoteip, remoteport, localip,localport, timeout)
except AddressBindingError:
  pass
else:
  log("Did not get AddressBindingError connecting to a non-local IP.",'\n')


