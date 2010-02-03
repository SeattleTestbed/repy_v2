"""
   Author: Justin Cappos

   Start Date: 27 June 2008

   Description:

   This is a collection of communications routines that provide a programmer 
   with a reasonable environment.   This is used by repy.py to provide a 
   highly restricted (but usable) environment.
"""

import restrictions
import socket

# Armon: Used to check if a socket is ready
import select

# socket uses getattr and setattr.   We need to make these available to it...
socket.getattr = getattr
socket.setattr = setattr


# needed to set threads for recvmess and waitforconn
import threading

# to force destruction of old sockets
import gc

# So I can exit all threads when an error occurs or do select
import harshexit

# Needed for finding out info about sockets, available interfaces, etc
import nonportable

# So I can print a clean traceback when an error happens
import tracebackrepy

# accounting
import nanny

# give me uniqueIDs for the comminfo table
import idhelper

# for sleep
import time 

# Armon: Used for decoding the error messages
import errno

# Armon: Used for getting the constant IP values for resolving our external IP
import repy_constants 

# The architecture is that I have a thread which "polls" all of the sockets
# that are being listened on using select.  If a connection
# oriented socket has a connection pending, or a message-based socket has a
# message pending, and there are enough events it calls the appropriate
# function.





# Table of communications structures:
# {'type':'UDP','localip':ip, 'localport':port,'function':func,'socket':s, outgoing:True, 'closing_lock':lockobj}
# {'type':'TCP','remotehost':None, 'remoteport':None,'localip':None,'localport':None, 'socket':s, 'function':func, outgoing:False, 'closing_lock':lockobj}

comminfo = {}

# If we have a preference for an IP/Interface this flag is set to True
user_ip_interface_preferences = False

# Do we allow non-specified IPs
allow_nonspecified_ips = True

# Armon: Specified the list of allowed IP and Interfaces in order of their preference
# The basic structure is list of tuples (IP, Value), IP is True if its an IP, False if its an interface
user_specified_ip_interface_list = []

# This list caches the allowed IP's
# It is updated at the launch of repy, or by calls to getmyip and update_ip_cache
# NOTE: The loopback address 127.0.0.1 is always permitted. update_ip_cache will always add this
# if it is not specified explicitly by the user
allowediplist = []
cachelock = threading.Lock()  # This allows only a single simultaneous cache update


# Determines if a specified IP address is allowed in the context of user settings
def ip_is_allowed(ip):
  """
  <Purpose>
    Determines if a given IP is allowed, by checking against the cached allowed IP's.
  
  <Arguments>
    ip: The IP address to search for.
  
  <Returns>
    True, if allowed. False, otherwise.
  """
  global allowediplist
  global user_ip_interface_preferences
  global allow_nonspecified_ips
  
  # If there is no preference, anything goes
  # same with allow_nonspecified_ips
  if not user_ip_interface_preferences or allow_nonspecified_ips:
    return True
  
  # Check the list of allowed IP's
  return (ip in allowediplist)


# Only appends the elem to lst if the elem is unique
def unique_append(lst, elem):
  if elem not in lst:
    lst.append(elem)
      
# This function updates the allowed IP cache
# It iterates through all possible IP's and stores ones which are bindable as part of the allowediplist
def update_ip_cache():
  global allowediplist
  global user_ip_interface_preferences
  global user_specified_ip_interface_list
  global allow_nonspecified_ips
  
  # If there is no preference, this is a no-op
  if not user_ip_interface_preferences:
    return
    
  # Acquire the lock to update the cache
  cachelock.acquire()
  
  # If there is any exception release the cachelock
  try:  
    # Stores the IP's
    allowed_list = []
  
    # Iterate through the allowed list, handle each element
    for (is_ip_addr, value) in user_specified_ip_interface_list:
      # Handle normal IP's
      if is_ip_addr:
        unique_append(allowed_list, value)
    
      # Handle interfaces
      else:
        try:
          # Get the IP's associated with the NIC
          interface_ips = nonportable.os_api.get_interface_ip_addresses(value)
          for interface_ip in interface_ips:
            unique_append(allowed_list, interface_ip)
        except:
          # Catch exceptions if the NIC does not exist
          pass
  
    # This will store all the IP's that we are able to bind to
    bindable_list = []
        
    # Try binding to every ip
    for ip in allowed_list:
      sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
      try:
        sock.bind((ip,0))
      except:
        pass # Not a good ip, skip it
      else:
        bindable_list.append(ip) # This is a good ip, store it
      finally:
        sock.close()

    # Add loopback
    unique_append(bindable_list, "127.0.0.1")
  
    # Update the global cache
    allowediplist = bindable_list
  
  finally:      
    # Release the lock
    cachelock.release()
  
########################### General Purpose socket functions #################

def is_already_connected_exception(exceptionobj):
  """
  <Purpose>
    Determines if a given error number indicates that the socket
    is already connected.

  <Arguments>
    An exception object from a network call.

  <Returns>
    True if already connected, false otherwise
  """
  # Get the type
  exception_type = type(exceptionobj)

  # Only continue if the type is socket.error
  if exception_type is not socket.error:
    return False

  # Get the error number
  errnum = exceptionobj[0]

  # Store a list of error messages meaning we are connected
  connected_errors = ["EISCONN", "WSAEISCONN"]

  # Convert the errno to and error string name
  try:
    errname = errno.errorcode[errnum]
  except Exception,e:
    # The error is unknown for some reason...
    errname = None
  
  # Return if the error name is in our white list
  return (errname in connected_errors)


def is_recoverable_network_exception(exceptionobj):
  """
  <Purpose>
    Determines if a given error number is recoverable or fatal.

  <Arguments>
    An exception object from a network call.

  <Returns>
    True if potentially recoverable, False if fatal.
  """
  # Get the type
  exception_type = type(exceptionobj)

  # socket.timeout is recoverable always
  if exception_type == socket.timeout:
    return True

  # Only continue if the type is socket.error or select.error
  elif exception_type != socket.error and exception_type != select.error:
    return False
  
  # Get the error number
  errnum = exceptionobj[0]

  # Store a list of recoverable error numbers
  recoverable_errors = ["EINTR","EAGAIN","EBUSY","EWOULDBLOCK","ETIMEDOUT","ERESTART",
                        "WSAEINTR","WSAEWOULDBLOCK","WSAETIMEDOUT","EALREADY","WSAEALREADY",
                       "EINPROGRESS","WSAEINPROGRESS"]

  # Convert the errno to and error string name
  try:
    errname = errno.errorcode[errnum]
  except Exception,e:
    # The error is unknown for some reason...
    errname = None
  
  # Return if the error name is in our white list
  return (errname in recoverable_errors)


# Determines based on exception if the connection has been terminated
def is_terminated_connection_exception(exceptionobj):
  """
  <Purpose>
    Determines if the exception is indicated the connection is terminated.

  <Arguments>
    An exception object from a network call.

  <Returns>
    True if the connection is terminated, False otherwise.
    False means we could not determine with certainty if the socket is closed.
  """
  # Get the type
  exception_type = type(exceptionobj)

  # We only want to continue if it is socket.error or select.error
  if exception_type != socket.error and exception_type != select.error:
    return False

  # Get the error number
  errnum = exceptionobj[0]

  # Store a list of errors which indicate connection closed
  connection_closed_errors = ["EPIPE","EBADF","EBADR","ENOLINK","EBADFD","ENETRESET",
                              "ECONNRESET","WSAEBADF","WSAENOTSOCK","WSAECONNRESET",]

  # Convert the errnum to an error string
  try:
    errname = errno.errorcode[errnum]
  except:
    # The error number is not defined...
    errname = None

  # Return whether the errname is in our pre-defined list
  return (errname in connection_closed_errors)


# Armon: This is used for semantics, to determine if we have a valid IP.
def is_valid_ip_address(ipaddr):
  """
  <Purpose>
    Determines if ipaddr is a valid IP address.
    Address 0.0.0.0 is considered valid.

  <Arguments>
    ipaddr: String to check for validity. (It will check that this is a string).

  <Returns>
    True if a valid IP, False otherwise.
  """
  # Argument must be of the string type
  if not type(ipaddr) == str:
    return False

  # A valid IP should have 4 segments, explode on the period
  parts = ipaddr.split(".")

  # Check that we have 4 parts
  if len(parts) != 4:
    return False

  # Check that each segment is a number between 0 and 255 inclusively.
  for part in parts:
    # Check the length of each segment
    digits = len(part)
    if digits >= 1 and digits <= 3:
      # Attempt to convert to an integer
      try:
        number = int(part)
        if not (number >= 0 and number <= 255):
          return False

      except:
        # There was an error converting to an integer, not an IP
        return False
    else:
      return False

  # At this point, assume the IP is valid
  return True

# Armon: This is used for semantics, to determine if the given port is valid
def is_valid_network_port(port, allowzero=False):
  """
  <Purpose>
    Determines if a given network port is valid. 

  <Arguments>
    port: A numeric type (this will be checked) port number.
    allowzero: Allows 0 as a valid port if true

  <Returns>
    True if valid, False otherwise.
  """
  # Check the type is int or long
  if not (type(port) == long or type(port) == int):
    return False

  return ((allowzero and port == 0) or (port >= 1 and port <= 65535))


# Constant prefix for comm handles.
COMM_PREFIX = "_COMMH:"

# Makes commhandles for networking functions
def generate_commhandle():
  """
  <Purpose>
    Generates a string commhandle that can be used to uniquely identify
    a socket, while providing a means of "pseudo" verification.

  <Returns>
    A string handle.
  """
  # Get a unique value from idhelper
  uniqueid = idhelper.getuniqueid()

  # Return the id prefixed by the COMM_PREFIX
  return (COMM_PREFIX + uniqueid)


# Helps determine if a commhandle is valid
def is_valid_commhandle(commhandle):
  """
  <Purpose>
    Determines if the given commhandle is potentially valid.
    This is not a guarentee of validity, e.g. the commhandle may not
    exist.

  <Arguments>
    commhandle:
      The handle to be checked for validity

  <Returns>
    True if the handle if valid, False otherwise.
  """
  # Check if the handle is a string, this is a requirement
  if type(commhandle) != str:
    return False

  # Return if the handle starts with the correct prefix
  # This way we are not relying on the format of idhelper.getuniqueid()
  return commhandle.startswith(COMM_PREFIX)


########################### SocketSelector functions #########################



# used to lock the methods that check to see if the thread is running
selectorlock = threading.Lock()

# is the selector thread started...
selectorstarted = False


#### helper functions

# return the table entry for this socketobject
def find_socket_entry(socketobject):
  for commhandle in comminfo.keys():
    if comminfo[commhandle]['socket'] is socketobject:
      return comminfo[commhandle], commhandle
  raise KeyError, "Can't find commhandle"




# wait until there is a free event
def wait_for_event(eventname):
  while True:
    try:
      nanny.tattle_add_item('events',eventname)
      break
    except Exception:
      # They must be over their event limit.   I'll sleep and check later
      time.sleep(.1)



def should_selector_exit():
  global selectorstarted

  # Let's check to see if we should exit...   False means "nonblocking"
  if selectorlock.acquire(False):

    # Check that selector started is true.   This should *always* be the case
    # when I enter this function.   This is to test for bugs in my code
    if not selectorstarted:
      # This will cause the program to exit and log things if logging is
      # enabled. -Brent
      tracebackrepy.handle_internalerror("SocketSelector is started when" +
          ' selectorstarted is False', 39)

    # Got the lock...
    for comm in comminfo.values():
      # I'm listening and waiting so all is well
      if not comm['outgoing']:
        break
    else:
      # there is no listening function so I should exit...
      selectorstarted = False
      # I'm exiting...
      nanny.tattle_remove_item('events',"SocketSelector")
      selectorlock.release()
      return True

    # I should continue
    selectorlock.release()
  return False
    




# This function starts a thread to handle an entry with a readable socket in 
# the comminfo table
def start_event(entry, handle,eventhandle):
  if entry['type'] == 'UDP':
    # some sort of socket error, I'll assume they closed the socket or it's
    # not important
    try:
      # NOTE: is 4096 a reasonable maximum datagram size?
      data, addr = entry['socket'].recvfrom(4096)
    except socket.error:
      # they closed in the meantime?
      nanny.tattle_remove_item('events',eventhandle)
      return

    # wait if we're over the limit
    if data:
      if is_loopback(entry['localip']):
        nanny.tattle_quantity('looprecv',len(data))
      else:
        nanny.tattle_quantity('netrecv',len(data))
    else:
      # no data...   Let's stop this...
      nanny.tattle_remove_item('events',eventhandle)
      return

      
    try:
      EventDeliverer(entry['function'],(addr[0], addr[1], data, handle), eventhandle).start()
    except:
      # This is an internal error I think...
      # This will cause the program to exit and log things if logging is
      # enabled. -Brent
      tracebackrepy.handle_internalerror("Can't start UDP EventDeliverer", 29)



  # or it's a TCP accept event...
  elif entry['type'] == 'TCP':
    try:
      realsocket, addr = entry['socket'].accept()
    except socket.error:
      # they closed in the meantime?
      nanny.tattle_remove_item('events',eventhandle)
      return
    
    # put this handle in the table
    newhandle = generate_commhandle()
    comminfo[newhandle] = {'type':'TCP','remotehost':addr[0], 'remoteport':addr[1],'localip':entry['localip'],'localport':entry['localport'],'socket':realsocket,'outgoing':True, 'closing_lock':threading.Lock()}
    # I don't think it makes sense to count this as an outgoing socket, does 
    # it?

    # Armon: Create the emulated socket after the table entry
    safesocket = emulated_socket(newhandle)

    try:
      EventDeliverer(entry['function'],(addr[0], addr[1], safesocket, newhandle, handle),eventhandle).start()
    except:
      # This is an internal error I think...
      # This will cause the program to exit and log things if logging is
      # enabled. -Brent
      tracebackrepy.handle_internalerror("Can't start TCP EventDeliverer", 23)


  else:
    # Should never get here
    # This will cause the program to exit and log things if logging is
    # enabled. -Brent
    tracebackrepy.handle_internalerror("In start event, Unknown entry type", 51)



# Armon: What is the maximum number of samples to perform per second?
# This is to prevent excessive sampling if there is a bad socket and
# select() returns before timing out
MAX_SAMPLES_PER_SEC = 10
TIME_BETWEEN_SAMPLES = 1.0 / MAX_SAMPLES_PER_SEC

# Check for sockets using select and fire up user event threads as needed.
#
# This class holds nearly all of the complexity in this module.   It's 
# basically just a loop that gets pending sockets (using select) and then
# fires up events that call user provided functions
class SocketSelector(threading.Thread):
  
  def __init__(self):
    threading.Thread.__init__(self, name="SocketSelector")


  # Gets a list of all the sockets which are ready to have
  # accept() called on them
  def get_acceptable_sockets(self):
    # get the list of socket objects we might have a pending request on
    requestlist = []
    for comm in comminfo.values():
      if not comm['outgoing']:
        requestlist.append(comm['socket'])

    # nothing to request.   We should loop back around and check if all 
    # sockets have been closed
    if requestlist == []:
      return []

    # Perform a select on these sockets
    try:
      # Call select
      (acceptable, not_applic, has_excp) = select.select(requestlist,[],requestlist,0.5)
    
      # Add all the sockets with exceptions to the acceptable list
      for sock in has_excp:
        if sock not in acceptable:
          acceptable.append(sock)

      # Return the acceptable list
      return acceptable
    
    # There was probably an exception on the socket level, check individually
    except:

      # Hold the ready sockets
      readylist = []

      # Check each requested socket
      for socket in requestlist:
        try:
          (accept_will_block, write_will_block) = socket_state(socket, "r")
          if not accept_will_block:
            readylist.append(socket)
        
        # Ignore errors, probably the socket is closed.
        except:
          pass

      # Return the ready list
      return readylist



  def run(self):
    # Keep track of the last sample time
    # updated when there are no ready sockets
    last_sample = 0

    while True:

      # I'll stop myself only when there are no active threads to monitor
      if should_selector_exit():
        return

      # If the last sample with 0 ready sockets was less than TIME_BETWEEN_SAMPLES
      # seconds ago, sleep a while. This is to prevent a tight loop from consuming
      # CPU time doing nothing.
      current_time = nonportable.getruntime()
      time_diff = current_time - last_sample
      if time_diff < TIME_BETWEEN_SAMPLES:
        time.sleep(TIME_BETWEEN_SAMPLES - time_diff)

      # Get all the ready sockets
      readylist = self.get_acceptable_sockets()

      # If there is nothing to do, potentially delay the next sample
      if len(readylist) == 0:
        last_sample = current_time

      # go through the pending sockets, grab an event and then start a thread
      # to handle the connection
      for thisitem in readylist:
        try: 
          commtableentry,commhandle = find_socket_entry(thisitem)
        except KeyError:
          # let's skip this one, it's likely it was closed in the interim
          continue

        # now it's time to get the event...   I'll loop until there is a free
        # event
        eventhandle = idhelper.getuniqueid()
        wait_for_event(eventhandle)

        # wait if already oversubscribed
        if is_loopback(commtableentry['localip']):
          nanny.tattle_quantity('looprecv',0)
        else:
          nanny.tattle_quantity('netrecv',0)

        # Now I can start a thread to run the user's code...
        start_event(commtableentry,commhandle,eventhandle)
      







# this gives an actual event to the user's code
class EventDeliverer(threading.Thread):
  func = None
  args = None
  eventid = None

  def __init__(self, f, a,e):
    self.func = f
    self.args = a
    self.eventid = e

    # Initialize with a custom and unique thread name
    threading.Thread.__init__(self,name=idhelper.get_new_thread_name(COMM_PREFIX))

  def run(self):
    try:
      self.func(*(self.args))
    except:
      # we probably should exit if they raise an exception in a thread...
      tracebackrepy.handle_exception()
      harshexit.harshexit(14)

    finally:
      # our event is going away...
      nanny.tattle_remove_item('events',self.eventid)
      




        
#### used by other threads to interact with the SocketSelector...


# private.   Check if the SocketSelector is running and start it if it isn't
def check_selector():
  global selectorstarted

  # acquire the lock. 
  if selectorlock.acquire():
    # If I've not started, then start me...
    if not selectorstarted:
      # wait until there is a free event...
      wait_for_event("SocketSelector")
      selectorstarted = True
      SocketSelector().start()

    # verify a thread with the name "SocketSelector" is running
    for threadobj in threading.enumerate():
      if threadobj.getName() == "SocketSelector":
        # all is well
        selectorlock.release()
        return
  
    # this is bad.   The socketselector went away...
    # This will cause the program to exit and log things if logging is
    # enabled. -Brent
    tracebackrepy.handle_internalerror("SocketSelector died", 59)




# return the table entry for this type of socket, ip, port 
def find_tip_entry(socktype, ip, port):
  for commhandle in comminfo.keys():
    if comminfo[commhandle]['type'] == socktype and comminfo[commhandle]['localip'] == ip and comminfo[commhandle]['localport'] == port:
      return comminfo[commhandle], commhandle
  return (None,None)



# Find a commhandle, given TIPO: type, ip, port, outgoing
def find_tipo_commhandle(socktype, ip, port, outgoing):
  for commhandle in comminfo.keys():
    if comminfo[commhandle]['type'] == socktype and comminfo[commhandle]['localip'] == ip and comminfo[commhandle]['localport'] == port and comminfo[commhandle]['outgoing'] == outgoing:
      return commhandle
  return None


# Find an outgoing TCP commhandle, given local ip, local port, remote ip, remote port, 
def find_outgoing_tcp_commhandle(localip, localport, remoteip, remoteport):
  for commhandle in comminfo.keys():
    if comminfo[commhandle]['type'] == "TCP" and comminfo[commhandle]['localip'] == localip \
    and comminfo[commhandle]['localport'] == localport and comminfo[commhandle]['remotehost'] == remoteip \
    and comminfo[commhandle]['remoteport'] == remoteport and comminfo[commhandle]['outgoing'] == True:
      return commhandle
  return None






######################### Simple Public Functions ##########################



# Public interface
def gethostbyname(name):
  """
   <Purpose>
      Provides information about a hostname. Calls socket.gethostbyname().
      Translate a host name to IPv4 address format. The IPv4 address is
      returned as a string, such as '100.50.200.5'. If the host name is an
      IPv4 address itself it is returned unchanged.

   <Arguments>
     name:
         The host name to translate.

   <Exceptions>
     NetworkAddressError (descends from NetworkError) if the address cannot
     be resolved.

   <Side Effects>
     None.

   <Resource Consumption>
     This operation consumes network bandwidth of 4K netrecv, 1K netsend.
     (It's hard to tell how much was actually sent / received at this level.)

   <Returns>
     The IPv4 address as a string.
  """

  restrictions.assertisallowed('gethostbyname', name)

  # charge 4K for a look up...   I don't know the right number, but we should
  # charge something.   We'll always charge to the netsend interface...
  nanny.tattle_quantity('netsend', 1024) 
  nanny.tattle_quantity('netrecv', 4096)

  try:
    return socket.gethostbyname(name)
  except socket.gaierror:
    raise NetworkAddressError("The name '%s' could not be resolved." % name)
  except TypeError:
    raise ArgumentError("gethostbyname() takes a string as argument.")



# Public interface
def getmyip():
  """
   <Purpose>
      Provides the external IP of this computer.   Does some clever trickery.

   <Arguments>
      None

   <Exceptions>
      As from socket.gethostbyname_ex()

   <Side Effects>
      None.

   <Returns>
      The localhost's IP address
      python docs for socket.gethostbyname_ex()
  """

  restrictions.assertisallowed('getmyip')
  # I got some of this from: http://groups.google.com/group/comp.lang.python/browse_thread/thread/d931cdc326d7032b?hl=en
  
  # Update the cache and return the first allowed IP
  # Only if a preference is set
  if user_ip_interface_preferences:
    update_ip_cache()
    # Return the first allowed ip, there is always at least 1 element (loopback)
    return allowediplist[0]
  
  # Initialize these to None, so we can detect a failure
  myip = None
  
  # It's possible on some platforms (Windows Mobile) that the IP will be
  # 0.0.0.0 even when I have a public IP and the external IP is up. However, if
  # I get a real connection with SOCK_STREAM, then I should get the real
  # answer.
  for conn_type in [socket.SOCK_DGRAM, socket.SOCK_STREAM]:
        
    # Try each stable IP  
    for ip_addr in repy_constants.STABLE_PUBLIC_IPS:  
      try:
        # Try to resolve using the current connection type and 
        # stable IP, using port 80 since some platforms panic
        # when given 0 (FreeBSD)
        myip = get_localIP_to_remoteIP(conn_type, ip_addr, 80)
      except (socket.error, socket.timeout):
        # We can ignore any networking related errors, since we want to try 
        # the other connection types and IP addresses. If we fail,
        # we will eventually raise an exception anyways.
        pass
      else:
        # Return immediately if the IP address is good
        if myip != None and myip != '' and myip != "0.0.0.0": 
          return myip


  # Since we haven't returned yet, we must have failed.
  # Raise an exception, we must not be connected to the internet
  raise Exception("Cannot detect a connection to the Internet.")



def get_localIP_to_remoteIP(connection_type, external_ip, external_port=80):
  """
  <Purpose>
    Resolve the local ip used when connecting outbound to an external ip.
  
  <Arguments>
    connection_type:
      The type of connection to attempt. See socket.socket().
    
    external_ip:
      The external IP to attempt to connect to.
      
    external_port:
      The port on the remote host to attempt to connect to.
  
  <Exceptions>
    As with socket.socket(), socketobj.connect(), etc.
  
  <Returns>
    The locally assigned IP for the connection.
  """
  # Open a socket
  sockobj = socket.socket(socket.AF_INET, connection_type)

  try:
    sockobj.connect((external_ip, external_port))

    # Get the local connection information for this socket
    (myip, localport) = sockobj.getsockname()
      
  # Always close the socket
  finally:
    sockobj.close()
  
  return myip




###################### Shared message / connection items ###################


# Used to decide if an IP is the loopback IP or not.   This is needed for 
# accounting
def is_loopback(host):
  if not host.startswith('127.'):
    return False
  if len(host.split('.')) != 4:
    return False

  for number in host.split('.'):
    for char in number:
      if char not in '0123456789':
        return False

    try:
      if int(number) > 255 or int(number) < 0:
        return False
    except ValueError:
      return False
 
  return True









# Public interface !!!
def stopcomm(commhandle):
  """
   <Purpose>
      Stop handling events for a commhandle.   This works for both message and
      connection based event handlers.

   <Arguments>
      commhandle:
         A commhandle as returned by recvmess or waitforconn.

   <Exceptions>
      None.

   <Side Effects>
      This has an undefined effect on a socket-like object if it is currently
      in use.

   <Returns>
      Returns True if commhandle was successfully closed, False if the handle
      cannot be closed (i.e. it was already closed).
  """
  # Armon: Check that the handle is valid, an exception needs to be raised otherwise.
  if not is_valid_commhandle(commhandle):
    raise Exception("Invalid commhandle specified!")

  # if it has already been cleaned up, exit.
  if commhandle not in comminfo:
    # Armon: Semantic update, stopcomm needs to return True/False
    # since the handle does not exist we will return False
    return False

  restrictions.assertisallowed('stopcomm',comminfo[commhandle])

  cleanup(commhandle)
 
  # Armon: Semantic update, we successfully closed
  # if we made it here, since cleanup blocks.
  return True



# Armon: How frequently should we check for the availability of the socket?
RETRY_INTERVAL = 0.2 # In seconds

# Private
def cleanup(handle):
  # Armon: lock the cleanup so that only one thread will do the cleanup, but
  # all the others will block as well
  try:
    handle_lock = comminfo[handle]['closing_lock']
  except KeyError:
    # Handle a possible race condition, the socket has already been cleaned up.
    return
  
  # Acquire the lock       
  handle_lock.acquire()

  # if it's in the table then remove the entry and tattle...
  try:
    if handle in comminfo:
      # Armon: Shutdown the socket for writing prior to close
      # to unblock any threads that are writing
      try:
        comminfo[handle]['socket'].shutdown(socket.SHUT_WR)
      except:
        pass

      try:
        comminfo[handle]['socket'].close()
      except:
        pass
      
      info = comminfo[handle]  # Store the info

      if info['outgoing']:
        nanny.tattle_remove_item('outsockets', handle)
      else:
        nanny.tattle_remove_item('insockets', handle)
    
        # Armon: Block while the socket is not yet cleaned up
        # Get the socket info
        ip = info['localip']
        port = info['localport']
        socketType = info['type']
        tcp = (socketType == 'TCP') # Check if this is a TCP typed connection
    
        # Loop until the socket no longer exists
        # BUG: There exists a potential race condition here. The problem is that
        # the socket may be cleaned up and then before we are able to check for it again
        # another process binds to the ip/port we are checking. This would cause us to detect
        # the socket from the other process and we would block indefinately while that socket
        # is open.
        while nonportable.os_api.exists_listening_network_socket(ip,port, tcp):
          time.sleep(RETRY_INTERVAL)
      
      # Delete the entry last, so that other stopcomm operations will block
      del comminfo[handle]
    
  finally:
    # Always release the lock
    handle_lock.release()



####################### Message sending #############################



# Public interface!!!
def sendmessage(destip, destport, message, localip, localport):
  """
   <Purpose>
      Send a message to a host / port

   <Arguments>
      desthost:
         The host to send a message to
      destport:
         The port to send the message to
      message:
         The message to send
      localhost:
         The local IP to send the message from 
      localport:
         The local port to send the message from

   <Exceptions>
      AddressBindingError (descends NetworkError) when the local IP isn't
        a local IP.

      PortRestrictedException (descends ResourceException?) when the local
        port isn't allowed

      RepyArgumentError when the local IP and port aren't valid types
        or values

   <Side Effects>
      None.

   <Resource Consumption>
      This operation consumes 64 bytes + number of bytes of the message that
      were transmitted. This requires that the localport is allowed.

   <Returns>
      The number of bytes sent on success
  """

  # Check that if either localip or local port is specified, that both are
  if localport is None or localip is None:
    raise RepyArgumentError("Localip and localport must be specified.")
  if type(destip) is not str or type(destport) is not int or type(message) \
      is not str or type(localip) is not str or type(localport) is not int:
        raise RepyArgumentError("Invalid type of one or more arguments " + \
            "to sendmessage().")

  if not localip or localip == '0.0.0.0':
    raise RepyArgumentError("Can only bind to a single local ip.")
# JAC: removed since this breaks semantics
#  else:
#    if not is_valid_ip_address(localip):
#      raise Exception("Local IP address is invalid.")

# JAC: removed since this breaks semantics
#  if not is_valid_ip_address(desthost):
#    raise Exception("Destination host IP address is invalid.")
  
  if not is_valid_network_port(destport):
    raise RepyArgumentError("Destination port number must be an " + \
        "integer, between 1 and 65535.")

  if not is_valid_network_port(localport, True):
    raise RepyArgumentError("Local port number must be an integer, " + \
        "between 1 and 65535.")

  try:
    restrictions.assertisallowed('sendmess', desthost, destport, message, \
        localip, localport)
  except Exception, e:
    raise PortRestrictedException(str(e))

  if localport:
    nanny.tattle_check('messport', localport)

  # Armon: Check if the specified local ip is allowed
  # this check only makes sense if the localip is specified
  if localip and not ip_is_allowed(localip):
    raise PortRestrictedException("IP '" + str(localip) + "' is not allowed.")
  
  # If there is a preference, but no localip, then get one
  elif user_ip_interface_preferences and not localip:
    # Use whatever getmyip returns
    localip = getmyip()

  # this is used to track errors when trying to resend data
  firsterror = None

  if localip and localport:
    # let's see if the socket already exists...
    commtableentry, commhandle = find_tip_entry('UDP', localip, localport)
  else:
    # no, we'll skip
    commhandle = None

  # yes it does! let's use the existing socket
  if commhandle:

    # block in case we're oversubscribed
    if is_loopback(desthost):
      nanny.tattle_quantity('loopsend', 0)
    else:
      nanny.tattle_quantity('netsend', 0)

    # try to send using this socket
    try:
      bytessent = commtableentry['socket'].sendto(message, \
          (desthost, destport))
    except socket.error, e:
      # we're going to save this error in case we also get an error below.
      # This is likely to be the error we actually want to raise
      firsterror = e
      # should I really fall through here?
    else:
      # send succeeded, let's wait and return
      if is_loopback(desthost):
        nanny.tattle_quantity('loopsend', bytessent)
      else:
        nanny.tattle_quantity('netsend', bytessent)
      return bytessent
  

  # open a new socket
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 

  try:
    if localip:
      try:
        s.bind((localip,localport))
      except socket.error, e:
        if firsterror:
          raise AddressBindingError(str(firsterror))
        raise AddressBindingError(str(e))

    # wait if already oversubscribed
    if is_loopback(desthost):
      nanny.tattle_quantity('loopsend', 0)
    else:
      nanny.tattle_quantity('netsend', 0)

    bytessent = s.sendto(message, (desthost, destport))

    if is_loopback(desthost):
      nanny.tattle_quantity('loopsend', bytessent)
    else:
      nanny.tattle_quantity('netsend', bytessent)

    return bytessent

  finally:
    # close no matter what
    try:
      s.close()
    except:
      pass






# Public interface!!!
def recvmess(localip, localport, function):
  """
   <Purpose>
      Registers a function as an event handler for incoming messages

   <Arguments>
      localip:
         The local IP or hostname to register the handler on
      localport:
         The port to listen on
      function:
         The function that messages should be delivered to.   It should expect
         the following arguments: (remoteIP, remoteport, message, commhandle)

   <Exceptions>
      None.

   <Side Effects>
      Registers an event handler.

   <Returns>
      The commhandle for this event handler.
  """
  if not localip or localip == '0.0.0.0':
    raise Exception("Must specify a local IP address")

# JAC: removed since this breaks semantics
#  if not is_valid_ip_address(localip):
#    raise Exception("Local IP address is invalid.")

  if not is_valid_network_port(localport):
    raise Exception("Local port number must be an integer, between 1 and 65535.")

# Armon: Disabled function check since it is incompatible with functions that have
# a variable number of parameters. e.g. func1(*args)
#  # Check that the user specified function exists and takes 4 arguments
#  try:
#    # Get the argument count
#    arg_count = function.func_code.co_argcount
#    
#    # Is "self" the first argument?
#    object_function = function.func_code.co_varnames[0] == "self"   
#    
#    # We need the function to take 4 parameters, or 5 if its an object function
#    assert(arg_count == 4 or (arg_count == 5 and object_function))
#  except:
#    # If this is not a function, an exception will be raised.
#    raise Exception("Specified function must be valid, and take 4 parameters. See recvmess.")

  restrictions.assertisallowed('recvmess',localip,localport)

  nanny.tattle_check('messport',localport)
  
  # Armon: Check if the specified local ip is allowed
  if not ip_is_allowed(localip):
    raise Exception, "IP '"+localip+"' is not allowed."
  
  # Armon: Generate the new handle since we need it 
  # to replace the old handle if it exists
  handle = generate_commhandle()

  # check if I'm already listening on this port / ip
  # NOTE: I check as though there might be a socket open that is sending a
  # message.   This is nonsense since sendmess doesn't result in a socket 
  # persisting.   This is done so that if sockets for sendmess are cached 
  # later (as seems likely) the resulting code will not break.
  oldhandle = find_tipo_commhandle('UDP', localip, localport, False)
  if oldhandle:
    # if it was already there, update the function and return
    comminfo[oldhandle]['function'] = function

    # Armon: Create a new comminfo entry with the same info
    comminfo[handle] = comminfo[oldhandle]

    # Remove the old entry
    del comminfo[oldhandle]

    # We need nanny to substitute the old handle with the new one
    nanny.tattle_remove_item('insockets',oldhandle)
    nanny.tattle_add_item('insockets',handle)
    
    # Return the new handle
    return handle
    
  # we'll need to add it, so add a socket...
  nanny.tattle_add_item('insockets',handle)

  # get the socket
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((localip,localport))

    nonportable.preparesocket(s)
  except:
    try:
      s.close()
    except:
      pass
    nanny.tattle_remove_item('insockets',handle)
    raise

  # set up our table entry
  comminfo[handle] = {'type':'UDP','localip':localip, 'localport':localport,'function':function,'socket':s, 'outgoing':False, 'closing_lock':threading.Lock() }

  # start the selector if it's not running already
  check_selector()

  return handle













####################### Connection oriented #############################



# Public interface!!!
def openconn(desthost, destport,localip=None, localport=None,timeout=None):
  """
   <Purpose>
      Opens a connection, returning a socket-like object

   <Arguments>
      desthost:
         The host to open communcations with
      destport:
         The port to use for communication
      localip (optional):
         The local ip to use for the communication
      localport (optional):
         The local port to use for communication (0 for a random port)
      timeout (optional):
         The maximum amount of time to wait to connect

   <Exceptions>
      As from socket.connect, etc.

   <Side Effects>
      None.

   <Returns>
      A socket-like object that can be used for communication.   Use send, 
      recv, and close just like you would an actual socket object in python.
  """

  # Set a default timeout of 5 seconds if none is specified.
  if timeout is None:
    timeout = 5.0

  # Check that both localip and localport are given if either is specified
  if localip != None and localport == None or localport != None and localip == None:
    raise Exception("Localip and localport must be specified simultaneously.")

  # Set the default value of localip
  if not localip or localip == '0.0.0.0':
    localip = None
#  else:
# JAC: removed since this breaks semantics
    # Check that the localip is valid if given
#    if not is_valid_ip_address(localip):
#      raise Exception("Local IP address is invalid.")

  # Assign the default value of localport if none is given.
  if localport == None:
    localport = 0
 
# JAC: removed since this breaks semantics
  # Check the remote IP for validity
#  if not is_valid_ip_address(desthost):
#    raise Exception("Destination host IP address is invalid.")

  if not is_valid_network_port(destport):
    raise Exception("Destination port number must be an integer, between 1 and 65535.")

  # Allow the localport to be 0, which is the default.
  if not is_valid_network_port(localport, True):
    raise Exception("Local port number must be an integer, between 1 and 65535.")

  # Check that the timeout is a number, greater than 0
  if not (type(timeout) == float or type(timeout) == int or type(timeout) == long) or timeout <= 0.0:
    raise Exception("Timeout parameter must be a numeric value greater than 0.")

  # Armon: Check if the specified local ip is allowed
  # this check only makes sense if the localip is specified
  if localip and not ip_is_allowed(localip):
    raise Exception, "IP '"+str(localip)+"' is not allowed."

  # If there is a preference, but no localip, then get one
  elif user_ip_interface_preferences and not localip:
    # Use whatever getmyip returns
    localip = getmyip()

  restrictions.assertisallowed('openconn',desthost,destport,localip,localport)
  
  # Get our start time
  starttime = nonportable.getruntime()

  # Armon: Check for any pre-existing sockets. If they are being closed, wait for them.
  # This will also serve to check if repy has a pre-existing socket open on this same tuple
  exists = True
  while exists and nonportable.getruntime() - starttime < timeout:
    # Update the status
    (exists, status) = nonportable.os_api.exists_outgoing_network_socket(localip,localport,desthost,destport)
    if exists:
      # Check the socket state
      if "ESTABLISH" in status or "CLOSE_WAIT" in status:
        # Check if the socket is from this repy vessel
        handle = find_outgoing_tcp_commhandle(localip, localport, desthost, destport)
        
        message = "Network socket is in use by an external process!"
        if handle != None:
          message = " Duplicate handle exists with name: "+str(handle)
        
        raise Exception, message
      else:
        # Wait for socket cleanup
        time.sleep(RETRY_INTERVAL)
  else:
    # Check if a socket exists still and we timed out
    if exists:
      raise Exception, "Timed out checking for socket cleanup!"
        

  if localport:
    nanny.tattle_check('connport',localport)

  handle = generate_commhandle()

  # If allocation of an outsocket fails, we garbage collect and try again
  # -- this forces destruction of unreferenced objects, which is how we
  # free resources.
  try:
    nanny.tattle_add_item('outsockets',handle)
  except:
    gc.collect()
    nanny.tattle_add_item('outsockets',handle)

  
  try:
    s = get_real_socket(localip,localport)

  
    # add the socket to the comminfo table
    comminfo[handle] = {'type':'TCP','remotehost':None, 'remoteport':None,'localip':localip,'localport':localport,'socket':s, 'outgoing':True, 'closing_lock':threading.Lock()}
  except:
    # the socket wasn't passed to the user prog...
    nanny.tattle_remove_item('outsockets',handle)
    raise


  try:
    thissock = emulated_socket(handle)
    # We set a timeout before we connect.  This allows us to timeout slow 
    # connections...
    oldtimeout = comminfo[handle]['socket'].gettimeout()
 
    # Set the new timeout
    comminfo[handle]['socket'].settimeout(timeout)

    # Store exceptions until we exit the loop, default to timed out
    # in case we are given a very small timeout
    connect_exception = Exception("Connection timed out!")

    # Ignore errors and retry if we have not yet reached the timeout
    while nonportable.getruntime() - starttime < timeout:
      try:
        comminfo[handle]['socket'].connect((desthost,destport))
        break
      except Exception,e:
        # Check if the socket is already connected (EISCONN or WSAEISCONN)
        if is_already_connected_exception(e):
          break

        # Check if this is recoverable, only continue if it is
        elif not is_recoverable_network_exception(e):
          raise

        else:
          # Store the exception
          connect_exception = e

        # Sleep a bit, avoid excessive iterations of the loop
        time.sleep(0.2)
    else:
      # Raise any exception that was raised
      if connect_exception != None:
        raise connect_exception

    comminfo[handle]['remotehost']=desthost
    comminfo[handle]['remoteport']=destport
  
  except:
    cleanup(handle)
    raise
  else:
    # and restore the old timeout...
    comminfo[handle]['socket'].settimeout(oldtimeout)

  return thissock




# Public interface!!!
def waitforconn(localip, localport,function):
  """
   <Purpose>
      Waits for a connection to a port.   Calls function with a socket-like 
      object if it succeeds.

   <Arguments>
      localip:
         The local IP to listen on
      localport:
         The local port to bind to
      function:
         The function to call.   It should take five arguments:
         (remoteip, remoteport, socketlikeobj, thiscommhandle, maincommhandle)
         If your function has an uncaught exception, the socket-like object it
         is using will be closed.
         
   <Exceptions>
      None.

   <Side Effects>
      Starts an event handler that listens for connections.

   <Returns>
      A handle to the comm object.   This can be used to stop listening
  """
  if not localip or localip == '0.0.0.0':
    raise Exception("Must specify a local IP address")

# JAC: removed since this breaks semantics
#  if not is_valid_ip_address(localip):
#    raise Exception("Local IP address is invalid.")
  
  if not is_valid_network_port(localport):
    raise Exception("Local port number must be an integer, between 1 and 65535.")

  restrictions.assertisallowed('waitforconn',localip,localport)

  nanny.tattle_check('connport',localport)

  # Armon: Check if the specified local ip is allowed
  if not ip_is_allowed(localip):
    raise Exception, "IP '"+localip+"' is not allowed."

  # Get the new handle first, because we need to replace
  # the oldhandle if it exists to match semantics
  handle = generate_commhandle()
  
  # check if I'm already listening on this port / ip
  oldhandle = find_tipo_commhandle('TCP', localip, localport, False)
  if oldhandle:
    # if it was already there, update the function and return
    comminfo[oldhandle]['function'] = function

    # Armon: Create an entry for the handle, replicate the information
    comminfo[handle] = comminfo[oldhandle]
    
    # Remove the entry for the old socket
    del comminfo[oldhandle]

    # Un "tattle" the old handle, re-add the new handle
    nanny.tattle_remove_item('insockets',oldhandle)
    nanny.tattle_add_item('insockets',handle)

    # Give the new handle
    return handle
    
  # we'll need to add it, so add a socket...
  nanny.tattle_add_item('insockets',handle)

  # get the socket
  try:
    mainsock = get_real_socket(localip,localport)
    # NOTE: Should this be anything other than a hardcoded number?
    mainsock.listen(5)
    # set up our table entry
    comminfo[handle] = {'type':'TCP','remotehost':None, 'remoteport':None,'localip':localip,'localport':localport,'socket':mainsock, 'outgoing':False, 'function':function, 'closing_lock':threading.Lock()}
  except:
    nanny.tattle_remove_item('insockets',handle)
    raise


  # start the selector if it's not running already
  check_selector()

  return handle





# Private
def get_real_socket(localip=None, localport = None):

  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # reuse the socket if it's "pseudo-availible"
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


  if localip and localport:
    try:
      s.bind((localip,localport))
    except socket.error, e:
      # don't leak sockets
      s.close()
      raise Exception, e
    except:
      # don't leak sockets
      s.close()
      raise

  return s


# Checks if the given real socket would block
def socket_state(realsock, waitfor="rw", timeout=0.0):
  """
  <Purpose>
    Checks if the given socket would block on a send() or recv().
    In the case of a listening socket, read_will_block equates to
    accept_will_block.

  <Arguments>
    realsock:
              A real socket.socket() object to check for.

    waitfor:
              An optional specifier of what to wait for. "r" for read only, "w" for write only,
              and "rw" for read or write. E.g. if timeout is 10, and wait is "r", this will block
              for up to 10 seconds until read_will_block is false. If you specify "r", then
              write_will_block is always true, and if you specify "w" then read_will_block is
              always true.

    timeout:
              An optional timeout to wait for the socket to be read or write ready.

  <Returns>
    A tuple, (read_will_block, write_will_block).

  <Exceptions>
    As with select.select(). Probably best to wrap this with is_recoverable_network_exception
    and is_terminated_connection_exception. Throws an exception if waitfor is not in ["r","w","rw"]
  """
  # Check that waitfor is valid
  if waitfor not in ["rw","r","w"]:
    raise Exception, "Illegal waitfor argument!"

  # Array to hold the socket
  sock_array = [realsock]

  # Generate the read/write arrays
  read_array = []
  if "r" in waitfor:
    read_array = sock_array

  write_array = []
  if "w" in waitfor:
    write_array = sock_array

  # Call select()
  (readable, writeable, exception) = select.select(read_array,write_array,sock_array,timeout)

  # If the socket is in the exception list, then assume its both read and writable
  if (realsock in exception):
    return (False, False)

  # Return normally then
  return (realsock not in readable, realsock not in writeable)




# Public.   We pass these to the users for communication purposes
class emulated_socket:
  # This is an index into the comminfo table...

  commid = 0

  def __init__(self, handle):
    self.commid = handle

    # Armon: Get the real socket
    try:
      realsocket = comminfo[handle]['socket']

    # Shouldn't happen because my caller should create the table entry first
    except KeyError:
      raise Exception, "Internal Error. No table entry for new socket!"

    # Make the socket non-blocking
    realsocket.setblocking(0)

    try:
      # Store the send buffer size.   We'll send less than this to avoid a bug
      comminfo[handle]['sendbuffersize'] = realsocket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)

    # Really shouldn't happen.   We just checked!
    except KeyError:
      raise Exception, "Internal Error. No table entry when looking up sendbuffersize for new socket!"


    return None 




  def close(self):
    """
      <Purpose>
        Closes a socket.   Pending remote recv() calls will return with the 
        remaining information.   Local recv / send calls will fail after this.

      <Arguments>
        None

      <Exceptions>
        None

      <Side Effects>
        Pending local recv calls will either return or have an exception.

      <Returns>
        True if this is the first close call to this socket, False otherwise.
    """
    # prevent TOCTOU race with client changing the object's properties
    mycommid = self.commid
    restrictions.assertisallowed('socket.close')
    
    # Armon: Semantic update, return whatever stopcomm does.
    # This will result in socket.close() returning a True/False indicator
    return stopcomm(mycommid)



  def recv(self,bytes):
    """
      <Purpose>
        Receives data from a socket.   It may receive fewer bytes than 
        requested.   

      <Arguments>
        bytes: 
           The maximum number of bytes to read.   

      <Exceptions>
        Exception if the socket is closed either locally or remotely.

      <Side Effects>
        This call will block the thread until the other side calls send.

      <Returns>
        The data received from the socket (as a string).   If '' is returned,
        the other side has closed the socket and no more data will arrive.
    """
    # prevent TOCTOU race with client changing the object's properties
    mycommid = self.commid
    restrictions.assertisallowed('socket.recv',bytes)

    # I set this here so that I don't screw up accounting with a keyerror later
    try:
      this_is_loopback = is_loopback(comminfo[mycommid]['remotehost'])
    # they likely closed the connection
    except KeyError:
      raise Exception, "Socket closed"

    # wait if already oversubscribed
    if this_is_loopback:
      nanny.tattle_quantity('looprecv',0)
    else:
      nanny.tattle_quantity('netrecv',0)

    datarecvd = 0
    # loop until we recv the information (looping is needed for Windows)
    while True:
      try:
        # the timeout is needed so that if the socket is closed in another 
        # thread, we notice it
        # BUG: What should the timeout be?   What is the right value?
        #comminfo[mycommid]['socket'].settimeout(0.2)
        
        # Armon: Get the real socket
        realsocket = comminfo[mycommid]['socket']
	
        # Check if the socket is ready for reading
        (read_will_block, write_will_block) = socket_state(realsocket, "r", 0.2)	
        if not read_will_block:
          datarecvd = realsocket.recv(bytes)
          break

      # they likely closed the connection
      except KeyError:
        raise Exception, "Socket closed"

      # Catch all other exceptions, check if they are recoverable
      except Exception, e:
        # Check if this error is recoverable
        if is_recoverable_network_exception(e):
          continue

        # Otherwise, raise the exception
        else:
          # Check if this is a connection termination
          if is_terminated_connection_exception(e):
            raise Exception("Socket closed")
          else:
            raise

    # Armon: Calculate the length of the data
    data_length = len(datarecvd)
    
    # Raise an exception if there was no data
    if data_length == 0:
      raise Exception("Socket closed")

    # do accounting here...
    if this_is_loopback:
      nanny.tattle_quantity('looprecv',data_length)
    else:
      nanny.tattle_quantity('netrecv',data_length)

    return datarecvd



  def send(self,message):
    """
      <Purpose>
        Sends data on a socket.   It may send fewer bytes than requested.   

      <Arguments>
        message:
          The string to send.

      <Exceptions>
        Exception if the socket is closed either locally or remotely.

      <Side Effects>
        This call may block the thread until the other side calls recv.

      <Returns>
        The number of bytes sent.   Be sure not to assume this is always the 
        complete amount!
    """
    # prevent TOCTOU race with client changing the object's properties
    mycommid = self.commid
    restrictions.assertisallowed('socket.send',message)

    # I factor this out because we must do the accounting at the bottom of this
    # function and I want to make sure we account properly even if they close 
    # the socket right after their data is sent
    try:
      this_is_loopback = is_loopback(comminfo[mycommid]['remotehost'])
    except KeyError:
      raise Exception, "Socket closed!"

    # wait if already oversubscribed
    if this_is_loopback:
      nanny.tattle_quantity('loopsend',0)
    else:
      nanny.tattle_quantity('netsend',0)

    try:
      # Trim the message size to be less than the sendbuffersize.
      # This is a fix for http://support.microsoft.com/kb/823764
      message = message[:comminfo[mycommid]['sendbuffersize']-1]
    except KeyError:
      raise Exception, "Socket closed!"

    # loop until we send the information (looping is needed for Windows)
    while True:
      try:
        # Armon: Get the real socket
        realsocket = comminfo[mycommid]['socket']
	
        # Check if the socket is ready for writing, wait 0.2 seconds
        (read_will_block, write_will_block) = socket_state(realsocket, "w", 0.2)
        if not write_will_block:
          bytessent = realsocket.send(message)
          break
      
      except KeyError:
        raise Exception, "Socket closed"

      except Exception,e:
        # Determine if the exception is fatal
        if is_recoverable_network_exception(e):
          continue
        else:
          # Check if this is a conn. term., and give a more specific exception.
          if is_terminated_connection_exception(e):
            raise Exception("Socket closed")
          else:
            raise

    if this_is_loopback:
      nanny.tattle_quantity('loopsend',bytessent)
    else:
      nanny.tattle_quantity('netsend',bytessent)

    return bytessent


  # Checks if socket read/write operations will block
  def willblock(self):
    """
    <Purpose>
      Determines if a socket would block if send() or recv() was called.

    <Exceptions>
      Socket Closed if the socket has been closed.

    <Returns>
      A tuple, (recv_will_block, send_will_block) both are boolean values.

    """

    try:
      # Get the real socket
      realsocket = comminfo[self.commid]['socket']

      # Call into socket_state with no timout to return instantly
      return socket_state(realsocket)
    
    # The socket is closed or in the process of being closed...
    except KeyError:
      raise Exception, "Socket closed"

    except Exception, e:
      # Determine if the socket is closed
      if is_terminated_connection_exception(e):
        raise Exception("Socket closed")
      
      # Otherwise raise whatever we have
      else:
        raise



  def __del__(self):
    cleanup(self.commid)



# End of emulated_socket class
