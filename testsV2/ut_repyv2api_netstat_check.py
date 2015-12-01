# This unit test tests to see if netstat is installed on the machine

# If this unit test fails then other modules that performs checks
# over the network will fail
# network connections both incoming and outgoing 
# as well as viewing routing tables, interface statistics 
# become unverifiable
 

import portable_popen

try:
  # check if netstat exists
  netstat_process = portable_popen.Popen(["netstat", "-an"])
except Exception, e:
  raise Exception('Netstat failed internally ' + str(e))  
