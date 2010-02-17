#pragma repy

runtime = getruntime()
if runtime > 10:
  print "An immediate call to getruntime() > 10! ("+str(runtime)+")"
