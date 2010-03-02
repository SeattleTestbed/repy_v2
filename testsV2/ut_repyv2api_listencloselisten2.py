"""
Check that I can receive connections after stopping listening even with
connections going on...
"""
#pragma repy restrictions.twoports

localip = "127.0.0.1"
localport = 12345
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0


tcpserversocket = listenforconnection(targetip, targetport)

# Connect...
conn = openconnection(targetip, targetport, localip, localport, timeout)

conn.close()

# stop listening...
tcpserversocket.close()


# try to listen again and reconnect
tcpserversocket = listenforconnection(targetip, targetport)
conn = openconnection(targetip, targetport, localip, localport, timeout)

(ip, port, serverconn) = tcpserversocket.getconnection()

assert(ip == localip)
assert(port == localport)


conn.close()
serverconn.close()
tcpserversocket.close()
