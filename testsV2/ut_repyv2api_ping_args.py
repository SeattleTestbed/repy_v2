"""
This unit test checks that we get a RepyArgumentError
when providing bad arguments to ping.
"""
#pragma repy

def tryit(dest_ip,count):
  try:
    ping(dest_ip,count)
    log("Bad combination worked! IP:"+str(dest_ip)+" Count: "+str(count),'\n')
  except:
    pass

# Try some bad combos
tryit(None, None)
tryit("abcd", 3)
tryit("0.0.0.0", 3)
tryit("255.255.255.255", 12345)

tryit("127.0.0.1", 0)
tryit("127.0.0.1", 3.1415)
tryit("127.0.0.1", -2)