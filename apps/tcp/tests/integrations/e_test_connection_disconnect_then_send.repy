include tcp.repy

if callfunc == 'initialize':
  IP = '127.0.0.1' #  getmyip()
  PORT = 12345

  socket = Connection()
  socket.bind(IP, PORT)

def server():
  socket.listen()
  socket.accept()

if callfunc == 'initialize':
  # fork thread for server
  settimer(0, server, ())

  socket.connect(IP, PORT)
  socket.disconnect()

  # should raise NotConnected exception
  socket.send("hi")
  exitall()
