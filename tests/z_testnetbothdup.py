def foo_mess(ip,port,mess, ch):
  raise Exception, "Should not get here"

def noop_mess(ip,port,mess, ch):
  stopcomm(ch)

def foo_conn(ip,port,sockobj, ch,mainch):
  raise Exception, "Should not be here"

def noop_conn(ip, port, sockobj, ch, mainch):
  stopcomm(ch)
  stopcomm(mainch)


if callfunc == 'initialize':
  ip = getmyip()
  recvmess(ip,<messport>,foo_mess)
  recvmess(ip,<messport>,noop_mess)   # should replace foo
  waitforconn(ip,<connport>,foo_conn)
  waitforconn(ip,<connport>,noop_conn)  # should overwrite foo...

  sleep(.1)

  sendmess(ip,<messport>,'hi')
  sockobj = openconn(ip,<connport>)

  sockobj.close()

  

