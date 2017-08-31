"""
This unit test checks createthread will eventually throw a ResourceExhaustedError.
"""

#pragma repy restrictions.fixed

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
  log("Exceeded thread limit!",'\n')

exitall()
