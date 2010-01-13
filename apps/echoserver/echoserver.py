# Handle an incoming message
def got_message(srcip,srcport,mess,ch):
  sendmess(srcip,srcport,mess)


if callfunc == 'initialize':
  recvmess(getmyip(),54321,got_message)  

