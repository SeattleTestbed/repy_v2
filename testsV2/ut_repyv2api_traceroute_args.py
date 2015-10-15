# This tests all sorts of bad arguments to ensure they are caught

#pragma repy


# Try some bad combos
for args in [("abc",33434,15,1,1),
    ("0.0.0.0",33434,15,1,1),
    "255.255.255.255",33434,15,1,1),
    ("127.0.0.1",12345,15,1,1),
    ("127.0.0.1",1234567,15,1,1),
    ("127.0.0.1",33434,"15",1,1),
    ("127.0.0.1",33434,15,"1",1),
    ("127.0.0.1",33434,15,1,"1")]:
    try:
      traceroute(*args)
      log("Bad combination worked!" + '\n')
    except:
      pass