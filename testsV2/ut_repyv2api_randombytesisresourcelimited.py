"""
This test checks that randombytes throttles correctly.
The restriction allows 10000 bytes a second.   Each call to randombytes uses 
1024 bytes.

Thus, it should always take a full second to return.
"""

#pragma repy restrictions.fixed

start = getruntime()

for num in range(20):
  data = randombytes()

end = getruntime()

if end-start < 1:
  log("randombytes returned too quickly! Took: "+str(end-start),'\n')

if end-start > 1.5:
  log("randombytes took too long to return! Took: "+str(end-start),'\n')


