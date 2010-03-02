"""
Check that I can open two connections to a listening socket at a time
"""
#pragma repy restrictions.threeports

localip = "127.0.0.1"
localport1 = 12345
localport2 = 12347
targetip = "127.0.0.1"
targetport = 12346
timeout = 1.0


tcpserversocket = listenforconnection(targetip, targetport)

conn1 = openconnection(targetip, targetport, localip, localport1, timeout)


(ip, port, serverconn1) = tcpserversocket.getconnection()
assert(ip == localip)
assert(port == localport1)

conn2 = openconnection(targetip, targetport, localip, localport2, timeout)
(ip, port, serverconn2) = tcpserversocket.getconnection()

assert(ip == localip)
assert(port == localport2)


conn1.close()
serverconn1.close()
conn2.close()
serverconn2.close()
