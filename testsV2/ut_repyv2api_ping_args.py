"""
This unit test checks that we get a RepyArgumentError
when providing bad arguments to ping.
"""
#pragma repy


# Try some bad combos
for args in [[None, None, None], ["abcd", 3, 3], ["0.0.0.0", 3, 3], 
    ["255.255.255.255", 3, 3],["127.0.0.1", 0, 3], ["127.0.0.1", 3.1415, 3], 
    ["127.0.0.1", -2, 3],["127.0.0.1", 3, 0], ["127.0.0.1", 3, 3.1415], 
    ["127.0.0.1", 3, -2],[]]:
    try:
      ping(*args)
      log("Bad combination worked!" + str(args) + '\n')
    except:      
      pass
