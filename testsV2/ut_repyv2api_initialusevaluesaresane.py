"""
This unit test checks the usage values returned by getresources.

We check that:
  1) Initial CPU use is sane
  2) Initial usage of most resources is 0
  3) Initial memory usage is sane
"""

#pragma repy restrictions.fixed

# Call getreources to get the initial values
limits, init_usage, stoptimes = getresources()

# Check that the threadcpu and cpu are sane
# We know our runtime, so the maximum CPU time is
# roughly run_time * cpu_limit * 2
# The *2 is because CPU restrictions are not setup at first.
max_time = getruntime() * limits["cpu"] * 2

if init_usage["cpu"] > max_time:
  log("Initial CPU use too high! Should be less than: "+str(max_time)+" is: "+str(init_usage["cpu"]),'\n')
if init_usage["threadcpu"] > max_time:
  log("Initial Thread CPU use too high! Should be less than: "+str(max_time)+" is: "+str(init_usage["threadcpu"]),'\n')

# Our initial memory should be reasonable. At least 4 MB?
if init_usage["memory"] < 4000000:
  log("Initial Memory Usage is unreasonably low! Expect at least 4MB, using: "+str(init_usage["memory"]),'\n')

# Our event usage should be 1
if init_usage["events"] != 1:
  log("Initial event usage should be 1! Using: "+str(init_usage["events"]),'\n')

# The other stuff should all be 0 now
expected_zero = ["filewrite", "fileread", "filesopened", "insockets", "outsockets", "netsend",
                 "netrecv", "loopsend", "looprecv", "lograte", "random", "messport", "connport"]

for resource in expected_zero:
  usage = init_usage[resource]
  if type(usage) in [float,int] and usage != 0:
    log("Resource '"+resource+"' utilization should be 0! Is: "+str(usage),'\n')
  if type(usage) in [set,list] and len(usage) != 0:
     log("Resource '"+resource+"' utilization should be 0! Is: "+str(usage),'\n')

