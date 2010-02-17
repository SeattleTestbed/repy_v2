"""
This unit test checks the sendmessage() API call.
"""

#pragma repy


# Check listenformessage() typechecks
try:
  s = listenformessage(5, 12345)
except RepyException:
  pass
else:
  print 'listenformessage shouldn\'t allow invalid ip/port types'

try:
  s = listenformessage('127.0.0.1', "str")
except RepyException:
  pass
else:
  print 'listenformessage shouldn\'t allow invalid ip/port types'

s = listenformessage('127.0.0.1', 12345)

data = "HI"*8

# Check sendmessage() typechecks
for attempt in [\
    (2, 12345, data, '127.0.0.1', 12345), \
    ('127.0.0.1', "str", data, '127.0.0.1', 12345), \
    ('127.0.0.1', 12345, 6, '127.0.0.1', 12345), \
    ('127.0.0.1', 12345, data, 6, 12345), \
    ('127.0.0.1', 12345, data, '127.0.0.1', "str")]:
  try:
    sendmessage(attempt[0], attempt[1], attempt[2], attempt[3], attempt[4])
    (rip, rport, mess) = s.getmessage()
  except RepyException:
    pass
  else:
    print "sendmessage shouldn't allow invalid types"

s.close()
