lst = [[1],[2],[3],[4]]

while getruntime() < 20:
  try:
   # Keep allocating memory
   lst = lst + lst + lst + lst
   
   raise Exception, "Junk!"
  except:
    pass

print "Should not get here!"
