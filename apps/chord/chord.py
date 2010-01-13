"""
   Author: Justin Cappos

   Start date: 9 July 2008

   Description:
     Chord-like (http://pdos.csail.mit.edu/chord/faq.html) routing system
     It was implemented using the pseudocode at: 
         http://ast-deim.urv.cat/wiki/Chord

     This only routes messages between nodes (i.e. no DHASH)

     I've pasted in a modified SHA1 python algorithm since they can't import
     SHA1

"""

################# SHA1 python code taken online and butchered.  
###### DO NOT USE digest()

#__date__    = '2004-11-17'


#import struct #, copy


# ======================================================================
# Bit-Manipulation helpers
#
#   _long2bytes() was contributed by Barry Warsaw
#   and is reused here with tiny modifications.
# ======================================================================

def _long2bytesBigEndian(n, blocksize=0):
  pass
#    """Convert a long integer to a byte string.
#
#    If optional blocksize is given and greater than zero, pad the front
#    of the byte string with binary zeros so that the length is a multiple
#    of blocksize.
#    """
#
#    # After much testing, this algorithm was deemed to be the fastest.
#    s = ''
#    pack = struct.pack
#    while n > 0:
#        s = pack('>I', n & 0xffffffffL) + s
#        n = n >> 32
#
#    # Strip off leading zeros.
#    for i in range(len(s)):
#        if s[i] <> '\000':
#            break
#    else:
#        # Only happens when n == 0.
#        s = '\000'
#        i = 0
#
#    s = s[i:]
#
#    # Add back some pad bytes. This could be done more efficiently
#    # w.r.t. the de-padding being done above, but sigh...
#    if blocksize > 0 and len(s) % blocksize:
#        s = (blocksize - len(s) % blocksize) * '\000' + s
#
#    return s


def _bytelist2longBigEndian(list):
    "Transform a list of characters into a list of longs."

    imax = len(list)/4
    hl = [0L] * imax

    j = 0
    i = 0
    while i < imax:
        b0 = long(ord(list[j])) << 24
        b1 = long(ord(list[j+1])) << 16
        b2 = long(ord(list[j+2])) << 8
        b3 = long(ord(list[j+3]))
        hl[i] = b0 | b1 | b2 | b3
        i = i+1
        j = j+4

    return hl


def _rotateLeft(x, n):
    "Rotate x (32 bit) left n bits circularly."

    return (x << n) | (x >> (32-n))


# ======================================================================
# The SHA transformation functions
#
# ======================================================================

def f0_19(B, C, D):
    return (B & C) | ((~ B) & D)

def f20_39(B, C, D):
    return B ^ C ^ D

def f40_59(B, C, D):
    return (B & C) | (B & D) | (C & D)

def f60_79(B, C, D):
    return B ^ C ^ D


f = [f0_19, f20_39, f40_59, f60_79]

# Constants to be used
K = [
    0x5A827999L, # ( 0 <= t <= 19)
    0x6ED9EBA1L, # (20 <= t <= 39)
    0x8F1BBCDCL, # (40 <= t <= 59)
    0xCA62C1D6L  # (60 <= t <= 79)
    ]

class sha:
    "An implementation of the MD5 hash function in pure Python."

    def __init__(self):
        "Initialisation."
        
        # Initial message length in bits(!).
        self.length = 0L
        self.count = [0, 0]

        # Initial empty message as a sequence of bytes (8 bit characters).
        self.input = []

        # Call a separate init function, that can be used repeatedly
        # to start from scratch on the same object.
        self.init()


    def init(self):
        "Initialize the message-digest and set all fields to zero."

        self.length = 0L
        self.input = []

        # Initial 160 bit message digest (5 times 32 bit).
        self.H0 = 0x67452301L
        self.H1 = 0xEFCDAB89L
        self.H2 = 0x98BADCFEL
        self.H3 = 0x10325476L
        self.H4 = 0xC3D2E1F0L

    def _transform(self, W):

        for t in range(16, 80):
            W.append(_rotateLeft(
                W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16], 1) & 0xffffffffL)

        A = self.H0
        B = self.H1
        C = self.H2
        D = self.H3
        E = self.H4

        """
        This loop was unrolled to gain about 10% in speed
        for t in range(0, 80):
            TEMP = _rotateLeft(A, 5) + f[t/20] + E + W[t] + K[t/20]
            E = D
            D = C
            C = _rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL
        """

        for t in range(0, 20):
            TEMP = _rotateLeft(A, 5) + ((B & C) | ((~ B) & D)) + E + W[t] + K[0]
            E = D
            D = C
            C = _rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(20, 40):
            TEMP = _rotateLeft(A, 5) + (B ^ C ^ D) + E + W[t] + K[1]
            E = D
            D = C
            C = _rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(40, 60):
            TEMP = _rotateLeft(A, 5) + ((B & C) | (B & D) | (C & D)) + E + W[t] + K[2]
            E = D
            D = C
            C = _rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL

        for t in range(60, 80):
            TEMP = _rotateLeft(A, 5) + (B ^ C ^ D)  + E + W[t] + K[3]
            E = D
            D = C
            C = _rotateLeft(B, 30) & 0xffffffffL
            B = A
            A = TEMP & 0xffffffffL


        self.H0 = (self.H0 + A) & 0xffffffffL
        self.H1 = (self.H1 + B) & 0xffffffffL
        self.H2 = (self.H2 + C) & 0xffffffffL
        self.H3 = (self.H3 + D) & 0xffffffffL
        self.H4 = (self.H4 + E) & 0xffffffffL
    

    # Down from here all methods follow the Python Standard Library
    # API of the sha module.

    def update(self, inBuf):
        """Add to the current message.

        Update the md5 object with the string arg. Repeated calls
        are equivalent to a single call with the concatenation of all
        the arguments, i.e. m.update(a); m.update(b) is equivalent
        to m.update(a+b).

        The hash is immediately calculated for all full blocks. The final
        calculation is made in digest(). It will calculate 1-2 blocks,
        depending on how much padding we have to add. This allows us to
        keep an intermediate value for the hash, so that we only need to
        make minimal recalculation if we call update() to add more data
        to the hashed string.
        """

        leninBuf = long(len(inBuf))

        # Compute number of bytes mod 64.
        index = (self.count[1] >> 3) & 0x3FL

        # Update number of bits.
        self.count[1] = self.count[1] + (leninBuf << 3)
        if self.count[1] < (leninBuf << 3):
            self.count[0] = self.count[0] + 1
        self.count[0] = self.count[0] + (leninBuf >> 29)

        partLen = 64 - index

        if leninBuf >= partLen:
            self.input[index:] = list(inBuf[:partLen])
            self._transform(_bytelist2longBigEndian(self.input))
            i = partLen
            while i + 63 < leninBuf:
                self._transform(_bytelist2longBigEndian(list(inBuf[i:i+64])))
                i = i + 64
            else:
                self.input = list(inBuf[i:leninBuf])
        else:
            i = 0
            self.input = self.input + list(inBuf)


    def digest(self):
        """Terminate the message-digest computation and return digest.

        Return the digest of the strings passed to the update()
        method so far. This is a 16-byte string which may contain
        non-ASCII characters, including null bytes.
        """

        raise Exception, "Justin butchered this function because it called a function that used struct"
        H0 = self.H0
        H1 = self.H1
        H2 = self.H2
        H3 = self.H3
        H4 = self.H4
        input = [] + self.input
        count = [] + self.count

        index = (self.count[1] >> 3) & 0x3fL

        if index < 56:
            padLen = 56 - index
        else:
            padLen = 120 - index

        padding = ['\200'] + ['\000'] * 63
        self.update(padding[:padLen])

        # Append length (before padding).
        bits = _bytelist2longBigEndian(self.input[:56]) + count

        self._transform(bits)

        # Store state in digest.
        digest = _long2bytesBigEndian(self.H0, 4) + \
                 _long2bytesBigEndian(self.H1, 4) + \
                 _long2bytesBigEndian(self.H2, 4) + \
                 _long2bytesBigEndian(self.H3, 4) + \
                 _long2bytesBigEndian(self.H4, 4)

        self.H0 = H0 
        self.H1 = H1 
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4
        self.input = input 
        self.count = count 

        return digest


    def longdigest(self):
        H0 = self.H0
        H1 = self.H1
        H2 = self.H2
        H3 = self.H3
        H4 = self.H4
        input = [] + self.input
        count = [] + self.count

        index = (self.count[1] >> 3) & 0x3fL

        if index < 56:
            padLen = 56 - index
        else:
            padLen = 120 - index

        padding = ['\200'] + ['\000'] * 63
        self.update(padding[:padLen])

        # Append length (before padding).
        bits = _bytelist2longBigEndian(self.input[:56]) + count

        self._transform(bits)

        value = (self.H0 << 128) + (self.H1 << 96) + (self.H2 << 64) + (self.H3 << 32) + self.H4

        self.H0 = H0 
        self.H1 = H1 
        self.H2 = H2
        self.H3 = H3
        self.H4 = H4
        self.input = input 
        self.count = count 

        return value




    def hexdigest(self):
        """Terminate and return digest in HEX form.

        Like digest() except the digest is returned as a string of
        length 32, containing only hexadecimal digits. This may be
        used to exchange the value safely in email or other non-
        binary environments.
        """
        return ''.join(['%02x' % ord(c) for c in self.digest()])

#    def copy(self):
#        """Return a clone object.
#
#        Return a copy ('clone') of the md5 object. This can be used
#        to efficiently compute the digests of strings that share
#        a common initial substring.
#        """
#
#        return copy.deepcopy(self)


# ======================================================================
# Mimic Python top-level functions from standard library API
# for consistency with the md5 module of the standard library.
# ======================================================================

# These are mandatory variables in the module. They have constant values
# in the SHA standard.

digest_size = digestsize = 20
blocksize = 1

def new(arg=None):
    """Return a new sha crypto object.

    If arg is present, the method call update(arg) is made.
    """

    crypto = sha()
    if arg:
        crypto.update(arg)

    return crypto








################################## Data types used for marshalling


class Node():
  ip = None
  port = None
  def __init__(self,foo=None):
    if foo == None:
      return

    self.ip, p = foo.split(':')
    self.port = int(p)
    
  def __repr__(self):
    return self.ip + ":"+str(self.port)



class NodeandId():
  node = None
  id = None
  def __init__(self,foo=None):
    if foo == None or foo=='None':
      return
    n, i = foo.split('@')
    self.node = Node(n)
    self.id = long(i)   # convert to long?
    
  def __repr__(self):
    if self.node==None:
      return 'None'
    return str(self.node) + "@"+str(self.id)



class Token():
  mystring = None
  def __init__(self,mystr):
    self.mystring = mystr
    
  def __repr__(self):
    return self.mystring

  def len(self):
    return len(self.mystring.split('!'))

  def pop(self):
    if self.len() == 0:
      raise Exception, "Error popping a token"

    if self.len() == 1:
      oldstring = self.mystring
      self.mystring = ''
      return oldstring
      
    firstbit, self.mystring = self.mystring.split('!',1)
    return firstbit

  def push(self, tokendata):
    self.mystring = tokendata + "!"+self.mystring

  def isempty(self):
    return self.mystring == ''






############### Utilities

# get the hash for a value
def do_hash(value):
  testobj = sha()
  testobj.update(str(value))
  return testobj.longdigest()



# is a key between a and b (a-inclusive)
def is_between(key, start,stop):
  k = long(key)
  a = long(start)
  b = long(stop)

  # Should be false for a==b
  if a <= b:
    return a <= k < b
  return k >= a or k < b


# needed for the finger table...
RINGBITS = 160
RINGSIZE = 2**RINGBITS


class RPCFailure(Exception):
  pass


def simulate_rpc(node, command, argument):
  # really need a mutex here...
  myrpcid = str(mycontext['rpcid'])
  mycontext['rpcid'] = mycontext['rpcid'] + 1
  # release mutex!

  send_message(node,command,myrpcid,argument)

  # we will wait at least 5 seconds
  for count in range(50):
    sleep(.1)

    # if I got my message return the value
    if myrpcid in mycontext['receivedmessage']:
      retval = mycontext['receivedmessage'][myrpcid]
      del mycontext['receivedmessage'][myrpcid]
      return retval
  else:
    raise RPCFailure, "RPC '"+myrpcid+"' Timeout"


def send_message(node, messagetype, token, value):
  # marshal the message and send it from my IP / port...
  # BUG: If I could send and receive from a port I am receiving on, I wouldn't
  # need to do this...
  sendmess(node.ip, node.port, messagetype+"|"+str(token)+"|"+str(value), mycontext['me'].ip, mycontext['me'].port)



###### The real functions needed by Chord





def incoming_message(remoteip, remoteport, message, commhandle):

  # BUG: If I could send and receive from a port I am receiving on, I wouldn't
  # need to do this...
  # unmarshal the message
  try:
    messagetype, tokendata, value = message.split('|')
  except ValueError:
    print "Error!   Got:",message
    return

  sourcenode = Node(str(remoteip)+":"+str(remoteport))

  messagetoken = Token(tokendata)

#  print "Got message:",messagetype, sourcenode, messagetoken, value

  # we got a response to a message we sent or forwarded...
  if messagetype == 'RESPONSE':
    token = messagetoken.pop()
    if not messagetoken.isempty():
      # we forwarded it, so forward it back
      priornode = Node(token)
      send_message(priornode, 'RESPONSE',messagetoken,value)
    else:
      # we initiated it
      mycontext['receivedmessage'][token] = value


  # say hi back (used to check if my predecessor is alive)
  elif messagetype == 'HI':
    send_message(sourcenode, 'RESPONSE', messagetoken, value)

  elif messagetype == 'notify':
    nai = NodeandId(value)

    # I am not my predecessor...
    if str(nai) == str(mycontext['me']):
      return
      
    if mycontext['predecessor'] == None or is_between(nai.id, mycontext['predecessor'].id+1, mycontext['me'].id):
      mycontext['predecessor'] = nai


  elif messagetype == 'predecessor':
    send_message(sourcenode, 'RESPONSE',messagetoken,mycontext['predecessor'])


  elif messagetype == 'find_successor':
    key = long(value)  
    # I know about it, because it's mine or I know all so send the successor...
    if is_between(key, mycontext['me'].id+1, mycontext['successor'].id+1) or str(mycontext['me'].id) == str(mycontext['successor'].id):
      send_message(sourcenode, 'RESPONSE',messagetoken,mycontext['successor'])
      return
    
    # or else we go fishing...
    naitoask = closest_preceding_node(key)
    messagetoken.push(str(sourcenode))
    if str(naitoask) == str(mycontext['me']):
      send_message(sourcenode, 'RESPONSE',messagetoken,mycontext['me'])
    else:
      send_message(naitoask.node, messagetype,messagetoken,key)


  elif messagetype == 'NAME':
    key = long(value)  

    if mycontext['predecessor'] != None and is_between(key, mycontext['predecessor'].id+1, mycontext['me'].id+1):
      send_message(sourcenode, 'RESPONSE',messagetoken,mycontext['myname'])
      return

    naitoask = closest_preceding_node(key)
    # if it's mine, respond...
    if str(mycontext['me']) == str(naitoask):
      send_message(sourcenode, 'RESPONSE',messagetoken,mycontext['myname'])
      return

    # or else we go fishing...
    messagetoken.push(str(sourcenode))
    send_message(naitoask.node, messagetype,messagetoken,key)



#  # I think this is only called locally and so should be a local procedure call
#  elif messagetype == 'closest_preceding_node':
#    # find the highest predecessor in my finger table
#    # I copy it so that if it is updated, I don't get an error...
#    for nai in mycontext['fingertable'][:]:
#      if nai == None:
#        continue
#      if is_between(key, mycontext['me'].id+1, nai.id):
#        send_message(sourcenode, 'RESPONSE',messagetoken,nai)
#        return
#
#    send_message(sourcenode, 'RESPONSE', messagetoken, mycontext['me'])
  
  else:
    print "Unknown message: ",messagetype



def closest_preceding_node(key):
  # try the successorlist first
  for nai in mycontext['successorlist'][:]:
    if is_between(key, mycontext['me'].id+1, nai.id):
      return nai

  # find the highest predecessor in my finger table
  # I copy it so that if it is updated, I don't get an error...
  for nai in mycontext['fingertable'][:]:
    if is_between(nai.id, mycontext['me'].id+1, key):
      return nai

  # I'm the closest
  return mycontext['me']




def create_ring():
  mycontext['predecessor'] = None
  mycontext['successor'] = mycontext['me']
    

def join(node):
  mycontext['predecessor'] = None
  mycontext['successor'] = NodeandId(simulate_rpc(node, 'find_successor',mycontext['me'].id))
  

# 
SUCCESSORLISTSIZE = 2



# returns at least the current nai on success, [] on failure
def get_predecessor_chain(stopid, startnai):
  pchain = [startnai]
  currentnai = startnai
  # We'll return once we have the list...
  while True:
    try:
      priornai = NodeandId(simulate_rpc(currentnai.node,'predecessor',''))
    except RPCFailure:
      # return what we have so far
      if currentnai == startnai:
        # error, couldn't ask anyone
        return []
      return pchain

    # we asked a node that doesn't know...
    if str(priornai) == 'None':
      return pchain

    # We're outside of our range...
    if not is_between(priornai.id, stopid, startnai.id):
      return pchain
    
    # otherwise add what we know and iterate...
    pchain.append(priornai)
    currentnai = priornai

  



# get a list of all nais in this range.   If failures occur, the list may be
# incomplete
def get_successor_nodes_in_range(key1, key2):

  for snai in mycontext['successorlist']:
    # find the first successor equal to or after key2
    if not is_between(snai.id,key1,key2):
      # Ask them who their predecessor is (until reaching known values or None)
      pchain = get_predecessor_chain(key1,snai)
      # if there was some response from at least the original node
      if pchain != []:
        return pchain
      # otherwise, we'll try another node...

  # things fall apart, the center does not hold
  print "Warning: Massive failures, increase SUCCESSORLISTSIZE...   "
  return []


def naiinlist(nai, thelist):
  for item in thelist:
    if str(nai) == str(item):
      return True
  return False


# used to sort...
def naicompare(a,b):
  # equal
  if str(a) == str(b):
    return 0

  # less
  if is_between(a.id, mycontext['me'].id+1, b.id):
    return -1
  else:
    return 1



# periodic function that verifies successors...
# use a successor list to stabilize
# I'm going to keep the successorlist ordered by key, so that it looks like:
# mysuccessor, a, b, c ...    where     me < mysuccessor < a < b < c...
def stabilize():

  # If my successor isn't in the list, it should be 
  if mycontext['successor'] not in mycontext['successorlist']:
    mycontext['successorlist'] = [mycontext['successor']] + mycontext['successorlist']

  # this will end up being my new successor list
  newlist = []

  # the previous id (I'll make this the bottom of the range)
  lastid = mycontext['me'].id
  # I'm going to build a list of all successor nodes using my prior list
  for nai in mycontext['successorlist']:
    thislist = get_successor_nodes_in_range(lastid+1, nai.id)
    lastid = nai.id
    for nai in thislist:
      if not naiinlist(nai, newlist):
        newlist.append(nai)

  # sort the list using a helper function
  newlist.sort(cmp=naicompare)

  # if my list is too small (this might append me, which is okay)...
  if len(newlist) < SUCCESSORLISTSIZE:
    sucnai = newlist[-1]
    nextnai = NodeandId(simulate_rpc(sucnai.node,'find_successor',sucnai.id+1))
    if not naiinlist(nextnai, newlist):
      newlist.append(nextnai)
  
#  print "STAB:",newlist


  mycontext['successorlist'] = newlist[:SUCCESSORLISTSIZE]
  mycontext['successor'] = mycontext['successorlist'][0]
  send_message(mycontext['successor'].node, 'notify','',mycontext['me'])

  settimer(STABILIZETIMER, stabilize, ())
      
  

# Old function...
def stabilize_simple():
  try:
    ret = simulate_rpc(mycontext['successor'].node,'predecessor','')
  except RPCFailure:
    print "RPC Failure during stabilize to: ",mycontext['successor'].node
    ret = None

  if ret != None and ret != 'None':

    naix = NodeandId(ret)

    # if it's closer or I'm my successor
    if is_between(naix.id, mycontext['me'].id+1, mycontext['successor'].id) or str(mycontext['me'].id) == str(mycontext['successor'].id):
      mycontext['successor'] = naix

  send_message(mycontext['successor'].node, 'notify','',mycontext['me'])
  
  # check every few seconds...
  settimer(STABILIZETIMER, stabilize_simple, ())




# the finger table is stored:
# 0 : node responsible for me.id + 2^159 % 2^160
# 1 : node responsible for me.id + 2^158 % 2^160
# 2 : node responsible for me.id + 2^157 % 2^160
# 3 : node responsible for me.id + 2^156 % 2^160
# ... 
# n : my successor         me.id + 2^(159-n) % 2^160 
# 
# nodes will not be stored multiple times.

# refresh the finger table entries...
def fix_fingers():
  
  newfingertable = []
  # walk the finger table 
  for bit in range(RINGBITS):
    key = (mycontext['me'].id + 2**((RINGBITS-1) - bit)) % RINGSIZE
    try: 
      newentry = NodeandId(simulate_rpc(mycontext['me'].node, 'find_successor', key))
    except RPCFailure:
      # let's stop here
      break

    # append if it's not in already and it's not me
    if not naiinlist(newentry, newfingertable) and str(newentry) != str(mycontext['me']):
      newfingertable.append(newentry)

    # if it's the end (we reached our successor...)
    if str(newentry) == str(mycontext['successor']):
      break

  newfingertable.sort(cmp=naicompare)
  mycontext['fingertable'] = newfingertable

  
  # check every ten seconds...
  settimer(FINGERSTIMER, fix_fingers, ())



# periodic check that the predecessor is okay
def check_predecessor():
  if mycontext['predecessor'] != None:
    try: 
      simulate_rpc(mycontext['predecessor'].node, 'HI','')
    except RPCFailure:
      mycontext['predecessor'] = None
  
  # check every few seconds...
  settimer(CHECKPREDECESSORTIMER, check_predecessor, ())



############## Functions for me...

def get_name(key):
  return simulate_rpc(mycontext['me'].node, 'NAME', key)

def get_name_periodicly(key):
  try:
    print get_name(key)
  except RPCFailure:
    pass
  settimer(15,get_name_periodicly,(key,))
  

# periodic status update
def print_status():
  get_name(0)
  print " ",mycontext['rpcid']
  print "status PR:", mycontext['predecessor']
  print "status ME:", mycontext['me']
  print "status SU:", mycontext['successor']
  print "fingertable:",mycontext['fingertable']
  settimer(PRINTTIMER, print_status, ())

def user_interface(remoteip, remoteport, mysock, thisch, mainch):
  
  desiredlocations = [(0,'0'),(2**158,'1/4'), (2**159,'1/2'), (2**159+2**158,'3/4')]
  locationdata = ''
  for location,locationstr in desiredlocations:
    try:
      thename =  get_name(location)
    except RPCFailure:
      thename = "unknown"
    locationdata = locationdata + (' (pos: %s, node: %s) ') % (locationstr,thename)

  mypage = """<HTML>
<TITLE>Chord-like DHT info</TITLE>
<BODY>
<H1>Table information</H1>
<p> Previous node: %s
<p> My node information: %s
<p> Successor node: %s
<p> Finger table: %s
<p> Nodes responsible for a few locations: %s
</BODY>
</HTML>""" % ( mycontext['predecessor'], mycontext['me'], mycontext['successor'], mycontext['fingertable'], locationdata)

  mysock.send(mypage)

  mysock.close()




PRINTTIMER = 10
STABILIZETIMER = 1
FINGERSTIMER = 2
CHECKPREDECESSORTIMER = 1

# a periodic process that cleans out failed and outdated rpc entries
def cleanrpcreturns():
  pass



# starts a chord instance.   Must be called with a node to bootstrap from...
def bootstrap(myport, bootstrapnode):
  # set me up
  mynode = Node()
  mynode.ip = getmyip()
  mynode.port = myport
  mycontext['me'] = NodeandId()
  mycontext['me'].id = do_hash(str(mynode))
  mycontext['me'].node = mynode
  print "My node is:",str(mycontext['me'])

  mycontext['rpcid'] = 0
  mycontext['receivedmessage'] = {}
  mycontext['fingertable'] = []
  mycontext['successorlist'] = []

  # listen for messages
  recvmess(mycontext['me'].node.ip, mycontext['me'].node.port, incoming_message)

  if bootstrapnode.strip() == '':
    print "Creating my own ring"
    # I should start a new ring
    create_ring()
  else:
    print "Joining a ring"
    # I should join another ring
    try: 
      join(Node(bootstrapnode))
    except RPCFailure:
      print "Cannot bootstrap to:",str(Node(bootstrapnode))
      exitall()

#  print_status()
  stabilize()
  check_predecessor()
  fix_fingers()
#  get_name_periodicly(0)
  try:
    waitforconn(mycontext['me'].node.ip, 9090, user_interface)
  except:
    pass
  


if callfunc == 'initialize':
  mycontext['myname'] = callargs[2]
  # I should be called with a port and a host to bootstrap from
  bootstrap(int(callargs[0]), callargs[1])


elif callfunc == 'exit':
  # do nothing!
  pass



