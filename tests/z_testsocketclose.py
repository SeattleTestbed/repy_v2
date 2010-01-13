"""
Author: Armon Dadgar
Description:
  This tests the behavior of sockets when close() is called and
  there is data in the recv buffer. "Bad" behavior would be if
  new_conn throws a "Socket closed" exception. Good behavior is
  a clean termination.

  When we call close(), it is possible that a TCP RST packet
  would be sent, and that the receiver of the RST packet
  dumps all the data in the recv buffer. Then, if a read
  were to be made on the recv buffer, it is empty and the
  connection is closed, so a "Socket closed" exception would
  be raised.

  However, if we do not send a TCP RST, and only send a FIN
  packet, then the data from the recv buffer can be read
  without causing a "Socket closed" exception.

  This test is to guarentee the "good" behavior, by which
  we avoid sending a RST packet.
"""

# Handle a new connection
def new_conn(ip,port,sock,ch1,ch2):
  # Values to send
  values = "1 2 3 4 5 " 

  # Send this
  sock.send(values)

  # Get the response
  sleep(0.4)
  response = sock.recv(4)

  # Done
  sock.close()
  stopcomm(ch2)

if callfunc == "initialize":
  # Get the ip
  ip = getmyip()

  # Setup listener
  waitforconn(ip,<connport>,new_conn)

  # Connect
  sock = openconn(ip,<connport>)

  # Read the first 2 numbers
  num1 = sock.recv(2)
  num2 = sock.recv(2)

  # Close now
  sock.send("bad!")
  sock.close()

