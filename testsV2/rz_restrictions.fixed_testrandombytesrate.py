"""
This test checks that randombytes throttles correctly.
The restriction allows 512 bytes a second, but randombytes uses 1024 bytes.

Thus, it should always take a full second to return.
"""

start = getruntime()

data = randombytes()

end = getruntime()

if end-start < 1:
  print "randombytes returned too quickly! Took: "+str(end-start)

if end-start > 1.5:
  print "randombytes took too long to return! Took: "+str(end-start)


