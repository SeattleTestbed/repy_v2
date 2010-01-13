
if callfunc=='initialize':
  myfo = open("junk_test.out","w")
  sleep(5)   # stop should notice junk.out and exit...
  raise Exception, "Should not reach here" 
  

