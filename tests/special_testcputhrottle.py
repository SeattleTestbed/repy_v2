# This is a special class of unit test for repy
# This test is designed to iterate for a specified
# number of iteration or time, and is used for checking
# proper CPU thottling behavior

ITERATE_TIME = "-t"
ITERATE_NUM = "-n"

# This does 1 "iteration"
# We need something that uses some CPU, but does not just block for a long time
# This just calculates 2^N for N (0,512)
def do_iteration():
  num = 0L
  for x in xrange(512):
    num = long(2**x)

if callfunc == "initialize":
  # Get our operating mode
  mode = callargs[0]
  
  # Get our value
  val = int(callargs[1])
  
  # Switch on mode
  if mode == ITERATE_TIME:
    start = getruntime()
    
    iterations = 0
    
    # Run until we reach the specified time limit
    while (getruntime() - start) < val:
      # Increment our iterations
      iterations += 1
      do_iteration()
      
    # We are done, print the iterations and exit
    print iterations
    exitall()
      
  elif mode == ITERATE_NUM:
    # Get our start time
    start = getruntime()
    
    # Loop for the number of specified iterations
    for x in xrange(val):
      do_iteration()
      
    # print our runtime and exit
    print (getruntime() - start)
    exitall()  
    
