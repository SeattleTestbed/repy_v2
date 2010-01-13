# Handle an incoming message
def got_message(srcip,srcport,mess,ch):
  print "Received message: '"+mess+"' from "+srcip+":"+str(srcport)
  sendmess(srcip,srcport,"Ping response from "+getmyip()+":"+callargs[0],getmyip(), int(callargs[0]))


if callfunc == 'initialize':
  if len(callargs) != 1:
    raise Exception("Must specify 'port' to wait for packets on")

  recvmess(getmyip(),int(callargs[0]),got_message)  

