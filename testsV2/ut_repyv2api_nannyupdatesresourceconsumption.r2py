"""

This unit test checks that nanny gives back resources properly.

We will do this by running an operation that will free 
some, but not all previously used resources, and then
comparing that difference to the expected difference.

"""

#pragma repy

start = getruntime()

# listfiles() costs 4096 fileread
listfiles()

# In case it would run too fast
sleep(0.001)

# Note that the resources are only given back when another method attempts to use that resource.
listfiles() # Another 4096 fileread, for a total of 8192 fileread used.

stop = getruntime()
lim, after_check, stops = getresources()

# The amount of resources replenished each second are supposed to be the amount
# listed in the limits from getresources(), multiplied by the number of seconds
# that passed since the previous call.

max_expected_difference = (stop-start)*lim["fileread"]

# The new cost is added only after the replenishing is complete.
# This gives a max difference of 4096
actual_difference = 8192 - after_check["fileread"] 

# The difference should be somewhere between 0 and the max difference.
if not (0 <= actual_difference <= min(4096, max_expected_difference)) :
  log("Resource consumption is not being updated properly! \n")
  log("Limit for fileread:" + str(lim['fileread']) + '\n')
  log("Maximum expected amount back: " + str(stop-start) + " * " + str(lim["fileread"]) + " = " + str(max_expected_difference) + '\n')
  log("Actual amount back: " + str(actual_difference) + '\n')
  log("Actual fileread: " + str(after_check["fileread"]) + '\n')
