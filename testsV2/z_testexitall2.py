"""
This unit test checks that a thread is launched and exitall is called
before another thread can print. If exitall works, then the main thread
will not be able to print.
"""

def thread():
  exitall()

createthread(thread)
sleep(.5)
print 'Print after exitall is called!'

