

# Function with variable arguments
def func1(*args):
  # Recognize the current clientnum
  mycontext[mycontext["clientnum"]] = True

# Function with exactly 4 args
def func2(ip,port,mesg,ch):
  mycontext[mycontext["clientnum"]] = True

# Check the same functions, from inside an object
class Thing():
  def func3(self,*args):
    mycontext[mycontext["clientnum"]] = True

  def func4(self,ip,port,mesg,ch):
    mycontext[mycontext["clientnum"]] = True

def timeout():
  print "Timed out!"
  print "mycontext:",mycontext
  exitall()

if callfunc == "initialize":
  ip = getmyip()
  port = <messport>

  # Setup the waitforconn
  waith = recvmess(ip,port,func1)

  # Setup mycontext
  mycontext["clientnum"] = 1
  
  # Set our timeout timer
  timeh = settimer(100,timeout,())

  # Try connecting 
  sendmess(ip,port,"ping")
  sleep(3)
  if not (1 in mycontext):
    print "Failed to connect when callback has variable number of arguments"

  # Switch the callback function
  mycontext["clientnum"] += 1
  waith = recvmess(ip,port,func2)
  sendmess(ip,port,"ping")
  sleep(3)
  if not (2 in mycontext):
    print "Failed to connect when callback has all parameters specified"

  # Get a "Thing" object
  th = Thing()
  mycontext["clientnum"] += 1
  waith = recvmess(ip,port,th.func3)
  sendmess(ip,port,"ping")
  sleep(3)
  if not (3 in mycontext):
    print "Failed to connect when callback is an object function with variable number of arguments"

  mycontext["clientnum"] += 1
  waith = recvmess(ip,port,th.func4)
  sendmess(ip,port,"ping")
  sleep(3)
  if not (4 in mycontext):
    print "Failed to connect when callback is an object function with all parameters specified."

  # Cancel the timer, cleanup and exit
  canceltimer(timeh)
  stopcomm(waith)

  exitall()



  

