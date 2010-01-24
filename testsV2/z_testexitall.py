"""
This unit test checks that a thread does not get to print before exitall is called.
If exitall works, the program will terminate immediately, and the print will not happen.
"""

def thread():
  sleep(0.1)
  print 'After exitall called'

createthread(thread)
exitall()
