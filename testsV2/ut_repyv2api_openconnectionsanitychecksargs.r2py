# This tests all sorts of bad arguments to ensure they are caught

#pragma repy

myip = getmyip()

try:
  # bad dest IP (must be num.num.num.num)
  openconnection('foo.com', 1000, myip, 12345, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 'foo.com' allowed for destip",'\n')


try:
  # bad dest IP (can't start with 0)
  openconnection('0.1.2.3', 1000, myip, 12345, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '0.1.2.3' allowed for destip",'\n')


try:
  # bad dest IP (can't start with 224-255)
  openconnection('234.1.2.3', 1000, myip, 12345, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '234.1.2.3' allowed for destip",'\n')


try:
  # bad local IP (can't start with 0)
  openconnection('1.2.3.4', 1000, '0.0.0.0', 12345, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '0.0.0.0' allowed for localip",'\n')


try:
  # bad dest port (can't be 0)
  openconnection('1.2.3.4', 0, myip, 12345, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '0' allowed for destport",'\n')


try:
  # bad dest port (can't be > 65535)
  openconnection('1.2.3.4', 65536, myip, 12345, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '65536' allowed for destport",'\n')

try:
  # bad local port (can't be > 65535)
  openconnection('1.2.3.4', 12345, myip, 5423452, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '5423452' allowed for localport",'\n')

try:
  # bad local port (can't be <=0)
  openconnection('1.2.3.4', 12345, myip, -5, 10)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '-5' allowed for localport",'\n')


try:
  # timeout must be positive
  openconnection('1.2.3.4', 12345, myip, 12345, -.0001)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment '-.0001' allowed for timeout",'\n')



try:
  # incorrect arg type
  openconnection('1.2.3.4', 12345, myip, 12345, None)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 'None' allowed for timeout",'\n')



