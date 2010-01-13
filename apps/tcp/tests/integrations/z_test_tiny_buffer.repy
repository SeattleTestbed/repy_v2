include tcp.repy

if callfunc == 'initialize':
  IP = getmyip()
  PORT = 12345
  MESSAGE = "hi"
  MAXLEN = 1 # tiny buffer

  socket = Connection()
  socket.bind(IP, PORT)
  socket.connect(IP, PORT)

  bytes = socket.send(MESSAGE)
  if bytes == 0:
    print "Expected some bytes"

  mess = socket.recv(MAXLEN)
  if mess != MESSAGE[0]:
    print "%s != %s" % (mess, MESSAGE[0])

  # get other tiny recv
  mess = socket.recv(MAXLEN)
  if mess != MESSAGE[1]:
    print "%s != %s" % (mess, MESSAGE[1])

  socket.disconnect()
  exitall()
