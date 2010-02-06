"""
This unit test checks createthread will eventually throw a ResourceExhaustedError.
"""

MAX_EVENTS = 9

def thread():
  sleep(60)

for x in xrange(MAX_EVENTS):
  createthread(thread)

try:
  createthread(thread)
except ResourceExhaustedError:
  pass
else:
  print "Exceeded thread limit!"

exitall()
