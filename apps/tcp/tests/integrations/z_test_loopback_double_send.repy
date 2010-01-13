include tcp.repy

if callfunc == 'initialize':
  IP = getmyip()
  PORT = 12345
  MESSAGE = "hi"
  MAXLEN = 4096

  socket = Connection()
  socket.bind(IP, PORT)
  socket.connect(IP, PORT)

  bytes = socket.send(MESSAGE)
  if bytes == 0:
    print "Expected some bytes"
  
  # send it twice
  bytes = socket.send(MESSAGE)
  if bytes == 0:
    print "Expected some bytes"

  mess = socket.recv(MAXLEN)
  if mess != MESSAGE + MESSAGE:
    print "%s != %s" % (mess, MESSAGE + MESSAGE)

  socket.disconnect()
  exitall()
