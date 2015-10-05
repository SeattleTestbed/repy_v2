# This tests all sorts of bad arguments to ensure they are caught

#pragma repy


try:
  get_network_packets('abc')
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 'abc' allowed for interface",'\n')

try:
  get_network_packets(123)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 123 allowed for interface",'\n')

try:
  get_network_packets(None)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment None allowed for interface",'\n')

try:
  get_network_packets('lo')
  pass
except RepyArgumentError:
  log("lo is regarded as illegal argment",'\n')