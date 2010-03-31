"""
Check that connecting from a non-local IP will result in an AddressBindingError
"""
#pragma repy

localip = getmyip()
localport = 12345
remoteport = 80
timeout = 0.00001
try:
  remoteip = gethostbyname('www.google.com')
except NetworkAddressError:
  log("Name lookup failed for www.google.com",'\n')
  exitall()

try:
  # I presume the timeout will happen before the connection
  openconnection(remoteip, remoteport, localip,localport, timeout)
except TimeoutError:
  pass
else:
  log("Did not have a TimeoutError when connecting to google in",timeout,"seconds",'\n')


