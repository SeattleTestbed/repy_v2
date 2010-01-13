# Handle an incoming message
def got_message(srcip,srcport,mess,ch):
  if srcip in mycontext['forwardIPs']:
    # forward the packet to the correct destination
    sendmess(mycontext['forwardIPs'][srcip],srcport,mess,getmyip(),srcport)


if callfunc == 'initialize':
  if len(callargs) != 3:
    raise Exception("Must specify 'IP1 IP2 port' to forward traffic")
  mycontext['forwardIPs'] = {}
  mycontext['forwardIPs'][callargs[0]] = callargs[1]
  mycontext['forwardIPs'][callargs[1]] = callargs[0]
  recvmess(getmyip(),int(callargs[2]),got_message)  

