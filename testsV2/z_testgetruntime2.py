#pragma repy

start = getruntime()
sleep(.2)
end = getruntime()
if end-start < .2:
  # It didn't sleep long enough or else my counter is wrong
  print "Elapsed time less than sleep time!"
