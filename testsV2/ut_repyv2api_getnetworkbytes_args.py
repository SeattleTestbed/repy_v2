# This tests all sorts of bad arguments to ensure they are caught

#pragma repy


try:
  get_network_bytes('abc')
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 'abc' allowed for interface",'\n')

try:
  get_network_bytes(123)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 123 allowed for interface",'\n')

try:
  get_network_bytes(None)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment None allowed for interface",'\n')

try:
  get_network_bytes('lo')
  pass
except RepyArgumentError:
  log("lo is regarded as illegal argment",'\n')