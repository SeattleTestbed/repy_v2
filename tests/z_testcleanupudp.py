# This test checks that the cleanup stopcomm does is complete
# We should not be able to do a sendmess after stopcomm finishes


def noop(ip,port,mesg,ch1):
  mycontext["inflight"] = False
  if mesg != "Should Get This":
    print mesg


if callfunc == "initialize":
  ip = getmyip()
  port = <messport>
  count = 0
  while count < 4:
    count += 1
    waith = recvmess(ip,port,noop)
    mycontext["inflight"] = True
    sendmess(ip,port,"Should Get This")
    sleep(1)
    if mycontext["inflight"]:
      print "Message not received in time!"
      exitall()
      
    stopcomm(waith)
    try:
      bytes = sendmess(ip,port,"Should NOT Get This")
    except:
      pass
    else:
      # Wait to see if the message arrives
      sleep(0.5)


