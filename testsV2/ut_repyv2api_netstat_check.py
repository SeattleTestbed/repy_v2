import portable_popen



try:
  # check if netstat exists
  netstat_process = portable_popen.Popen(["netstat", "-an"])
except Exception, e:
  raise Exception('Netstat failed internally ' + str(e))  
