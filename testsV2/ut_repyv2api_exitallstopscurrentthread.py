"""
This unit test checks that a thread does not get to log(before exitall is called.,'\n')
If exitall works, the program will terminate immediately, and the log(will not happen.,'\n')
"""

#pragma repy

def thread():
  sleep(0.1)
  log('After exitall called','\n')

createthread(thread)
exitall()
