# Handle an incoming message
def got_reply(srcip,srcport,mess,ch):
  print 'received:',mess,"from",srcip,srcport

if callfunc == 'initialize':
  # my port is a command line arg
  recvmess(getmyip(),43210,got_reply)  
  sendmess(getmyip(),54321,callargs[0], getmyip(), 43210)  
  # exit in one second
  settimer(1,exitall,())
  

