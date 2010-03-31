"""
Check that connecting from a non-local IP will result in an AddressBindingError
"""
#pragma repy restrictions.twoports

localip = "127.0.0.1"
localport = 12345
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0

tcpserversocket = listenforconnection(targetip, targetport)

conn1 = openconnection(targetip, targetport, localip, localport, timeout)

try:
  # Even though I'm connecting to something invalid, the AddressBindingError
  # has precedence
  openconnection(targetip, targetport, localip,localport, timeout)
except DuplicateTupleError:
  pass
else:
  log("Did not get DuplicateTupleError performing a redundant connection",'\n')


