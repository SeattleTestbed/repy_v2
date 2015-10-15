"""
This unit test checks that we get a RepyArgumentError
when providing bad arguments to ping.
"""
#pragma repy


# Try some bad combos
for args in [(None, None), ("abcd", 3), ("0.0.0.0", 3), ("255.255.255.255", 12345),
    ("127.0.0.1", 0), ("127.0.0.1", 3.1415), ("127.0.0.1", -2)]:
    try:
      ping(*args)
      log("Bad combination worked! IP:"+str(dest_ip)+" Count: "+str(count),'\n')
    except:
      pass
