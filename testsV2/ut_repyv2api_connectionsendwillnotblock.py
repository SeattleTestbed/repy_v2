"""
Check that send will not block in different situations...
"""
#pragma repy restrictions.twoports

localip = "127.0.0.1"
localport = 12345
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0

tcpserversocket = listenforconnection(targetip, targetport)

conn = openconnection(targetip, targetport, localip, localport, timeout)

# This should not raise an exception because it shouldn't block...
conn.send('hi')

(ip, port, serverconn) = tcpserversocket.getconnection()

assert(ip == localip)
assert(port == localport)


# Still shouldn't block
conn.send('hi')

# Server send shouldn't block either
serverconn.send('hi')

