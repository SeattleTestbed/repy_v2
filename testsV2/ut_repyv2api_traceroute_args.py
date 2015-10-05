# This tests all sorts of bad arguments to ensure they are caught

#pragma repy

def tryit(dest_name,port,max_hops,waittime,ttl):
  try:
    traceroute(dest_name,port,max_hops,waittime,ttl)
    log("Bad combination worked!" + '\n')
  except:
    pass

# Try some bad combos
#tryit("www.google.com",33434,15,1,1)
tryit("abc",33434,15,1,1)
tryit("0.0.0.0",33434,15,1,1)
tryit("255.255.255.255",33434,15,1,1)

tryit("127.0.0.1",12345,15,1,1)
tryit("127.0.0.1",1234567,15,1,1)

tryit("127.0.0.1",33434,"15",1,1)

tryit("127.0.0.1",33434,15,"1",1)

tryit("127.0.0.1",33434,15,1,"1")