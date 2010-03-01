"""
Check what happens with duplicates close
"""
#pragma repy restrictions.twoports

localip = "127.0.0.1"
localport = 12345
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0


tcpserversocket = listenforconnection(targetip, targetport)

conn = openconnection(targetip, targetport, localip, localport, timeout)


(ip, port, serverconn) = tcpserversocket.getconnection()

assert(ip == localip)
assert(port == localport)

# first call should be True, second is False...
assert(conn.close() == True)
assert(conn.close() == False)

# first call should be True, second is False...
assert(serverconn.close() == True)
assert(serverconn.close() == False)


