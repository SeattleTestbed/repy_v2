"""
This unit test checks the sendmessage() API call.
"""

s = listenformessage('127.0.0.1', 12345)

data = "HI"*8

sendmessage('127.0.0.1', 12345, data, '127.0.0.1', 12345)

(rip, rport, mess) = s.getmessage()

s.close()

if mess != data:
  print "Mismatch!"
