
lst = [1]

while getruntime() < 10:
  try:
   # Keep allocating memory
   lst = lst + lst
   
   raise Exception, "Junk!"
  except:
    pass

print "Should not get here!"