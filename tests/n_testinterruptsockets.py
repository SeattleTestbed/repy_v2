class SocketTimeout(Exception):
  pass


def clobbersocket(sockobj,mylock):
  # if I can acquire the lock without blocking, then close the socket to abort
  if mylock.acquire(False):
    sockobj.close()

# if it fails, the socket is closed...
def recv_timeout(sockobj, amount, timeout):
  # A lock I'll use for this attempt
  mylock = getlock()
  timerhandle = settimer(timeout,clobbersocket, (sockobj, mylock))
  try:
    retdata = sockobj.recv(amount)
  except Exception, e:
    # if it's not the timeout, reraise...
    if mylock.acquire(False):
      raise
    raise SocketTimeout
    
  # I acquired the lock, I should stop the timer because I succeeded...
  if mylock.acquire(False):
    # even if this isn't in time, the lock prevents a race condition 
    # this is merely an optimization to prevent the timer from ever firing...
    canceltimer(timerhandle)
    return retdata
  else:
    raise SocketTimeout




def newconn(IP, port, sockobj, thisch, mainch):

  try:
    recv_timeout(sockobj, mycontext['size'], mycontext['timeout'])
  except SocketTimeout:
    pass
  print "after"


if callfunc=='initialize':
  mycontext['size'] = 1024
  mycontext['timeout'] = 1
  mainch = waitforconn('127.0.0.1',<connport>, newconn)
  mysock = openconn('127.0.0.1',<connport>)
# check this out!!!
#  mysock.send("hi")
#  mysock.close()

  settimer(3, exitall,())

  while True:
    sleep(1)
   
