def foo(ip,port,sockobj, ch,mainch):
  
  data = sockobj.recv(4096)

  if data != "Hello":
    print 'Error: data did not match "Hello"'
    exitall()

  sockobj.send("bye")

  stopcomm(mainch)
  stopcomm(ch)


if callfunc == 'initialize':

  ip = getmyip()

  waitforconn(ip,<connport>,foo)
  sleep(.1)
  sockobj = openconn(ip,<connport>)

  # on many systems it will raise an exception here...   it also may or may
  # not raise an exception on different runs.
  waith = waitforconn(ip,<connport>,foo)
  sockobj.send("Hello")

  data = sockobj.recv(4096)

  if data != "bye":
    print 'Error: data did not match "bye"'
    exitall(1)

  sockobj.close()

  # Armon: If we do not explicitly stop the second waitforconn, we will never exit
  # This is because the second waitforconn has a different handle, and so when foo calls stopcomm(),
  # That is not actually stopping the listener
  stopcomm(waith)


