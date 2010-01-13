
import threading

class FileObj(object):
  def close(self):
    return False
  def readat(self, sizelimit, offset):
    return ""
  def writeat(self, data, offset):
    pass

class TCPSocketObj(object):
  def close(self):
    return False
  def send(self, message):
    return 1
  def recv(self, numbytes):
    return "x"

class TCPServerSocketObj(object):
  def close(self):
    return False
  def getconnection(self):
    return ('1.2.3.4', 1234, TCPSocketObj())

class UDPServerSocketObj(object):
  def close(self):
    return False
  def getmessage(self):
    return ('1.2.3.4', 1234, "x")

def gethostbyname(name):
  return '1.2.3.4'

def getmyip():
  return '1.2.3.4'

def sendmessage(destip, destport, message, localip, localport):
  return 1

def listenformessage(localip, localport):
  return UDPServerSocketObj()

def openconnection(destip, destport, localip, localport, timeout):
  return TCPSocketObj()

def listenforconnection():
  return TCPServerSocketObj()

def openfile(filename, create):
  return FileObj()

def listfiles():
  return ['a', 'b']

def removefile(filename):
  pass

def exitall():
  pass

def createlock():
  return threading.Lock()

def getruntime():
  return 1.23

def randombytes():
  return "a" * 1024

def createthread(function, *args):
  pass

def sleep(seconds):
  pass

def getthreadname():
  return 'x'

#def createvirtualnamespace(code, name):
#  pass

def getresources():
  return ({'a':'b'}, {'c':1})
