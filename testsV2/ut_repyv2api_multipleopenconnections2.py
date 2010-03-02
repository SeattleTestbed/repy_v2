"""
Check that I can open two connections to a listening socket at a time
Issue both before getting either connection
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
conn2 = openconnection(targetip, targetport, localip, localport2, timeout)


(ip1, port1, serverconn1) = tcpserversocket.getconnection()
(ip2, port2, serverconn2) = tcpserversocket.getconnection()

assert(ip1 == ip2 == localip)
# we don't know the connection order
assert(port1 == localport1 or port2 == localport1)
assert(port1 == localport2 or port2 == localport2)
assert(port1 != port2)

conn1.close()
serverconn1.close()
conn2.close()
serverconn2.close()
