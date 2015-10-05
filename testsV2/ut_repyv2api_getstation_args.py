# This tests all sorts of bad arguments to ensure they are caught

#pragma repy


try:
  get_station('abc')
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 'abc' allowed for interface",'\n')

try:
  get_station(123)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment 123 allowed for interface",'\n')

try:
  get_station(None)
except RepyArgumentError:
  # expected
  pass
else:
  log("Bad argment None allowed for interface",'\n')

try:
  get_station('wlan0')
  pass
except RepyArgumentError:
  log("wlan0 is regarded as illegal argment",'\n')