"""
  Author: Xuefeng Huang

  Start Date: 25 October 2015

  Description:

  This file provides a python interface to implement ping and traceroute 
  functionality. It is designed to let researchers do a wide range of network 
  measurements on home gateway.
   
"""

import nanny

import socket

import portable_popen # Import for Popen

import textops # Import seattlelib's text processing lib

import struct

import os # Provides some convenience functions

import emulcomm

import time

import select

# Get the exceptions
from exception_hierarchy import *

safe_open = open


##### Public Functions #####     
def traceroute(dest_ip, port, max_hops, waittime, ttl):
  """
  <Purpose>
    Return the route packets take to network host. Adapted from the original 
    at https://blogs.oracle.com/ksplice/entry/learning_by_doing_writing_your 

  <Arguments>
    dest_ip: The ip address to traceroute
    port: The port to traceroute
    max_hops: Maximum number of hops
    waittime: Set the time to wait for a response to a probe
    ttl: Set what TTL to start.

  <Exceptions>
    RepyArgumentError when the arguments aren't valid types or value
    or values

    ResourceForbiddenError when the local port isn't allowed

  <Resource Consumption>
    This operation consumes network bandwidth of 64 * max_hops bytes 
    netrecv, 64 * max_hops bytes netsend.

  <Side Effects>
    None

  <Returns>
    The result of traceroute
  """
  if type(dest_ip) is not str:
    raise RepyArgumentError("Provided dest_ip must be a string!")

  if type(port) is not int:
    raise RepyArgumentError("Provided port must be an integer!")

  if type(max_hops) is not int:
    raise RepyArgumentError("Provided max_hops must be an integer!")

  if type(waittime) is not int:
    raise RepyArgumentError("Provided waittime must be an integer!")

  if type(ttl) is not int:
    raise RepyArgumentError("Provided ttl must be an integer!")

  # Check the input arguments (sanity)
  if not emulcomm._is_valid_ip_address(dest_ip):
    raise RepyArgumentError("Provided dest_ip is not valid! IP: '" + dest_ip + "'")

  if not emulcomm._is_valid_network_port(port):
    raise RepyArgumentError("Provided port is not valid! Port: '" + str(port) + "'")

  if max_hops > 255 or max_hops < 0:
    raise RepyArgumentError("Provided max_hops: " + str(max_hops) + " should not be larger than 255.'")

  result = []
  
  # Account for the resources
  if emulcomm._is_loopback_ipaddr(dest_ip):
    nanny.tattle_quantity('loopsend', 64 * max_hops)
    nanny.tattle_quantity('looprecv', 64 * max_hops)
  else:
    nanny.tattle_quantity('netsend', 64 * max_hops)
    nanny.tattle_quantity('netrecv', 64 * max_hops)

  # Infinite loop until reach destination or TTL reach maximum.
  while True:
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
      socket.IPPROTO_ICMP)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
      socket.IPPROTO_UDP)
    send_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    recv_sock.bind(("", port))
    bytessent = send_sock.sendto("", (dest_ip, port))

    curr_addr = None
    curr_name = None

    try:
      # socket.recvfrom() gives back (data, address)
      recv_sock.settimeout(waittime)
      curr_addr = recv_sock.recvfrom(512)[1]
      curr_addr = curr_addr[0]
      try:
        curr_name = socket.gethostbyaddr(curr_addr)[0]
      except socket.error:
        curr_name = curr_addr
    except socket.error:
      pass

    send_sock.close()
    recv_sock.close()

    if curr_addr is not None:
      curr_host = "%s (%s)" % (curr_name, curr_addr)
    else:
      curr_host = "*"
    result.append("%d %s" % (ttl, curr_host)) 

    ttl += 1
    if curr_addr == dest_ip or ttl > max_hops:
      break

  return result

def ping(dest_ip, count, timeout):
  """
  <Purpose>
    A pure python ping implementation using raw sockets.

  <Arguments>
    dest_ip: the address to communicate with.
    count: Stop after sending count ECHO_REQUEST packets.
    timeout: Time to wait for a response, in seconds.

  <Exceptions>
    RepyArgumentError when the host name is not valid types
        or values

  <Side Effects>
    None

  <Resource Consumption>
    This operation consumes network bandwidth of 256 * count bytes netrecv, 
    256 * count bytes netsend.

  <Returns>
    ping statistics as a dict, such as { 'avg': '27.302', 'min': '14.861', 'host': 
    '192.168.1.1', 'max': '39.743', 'lost_rate': 0.0}
    `host`: the target hostname that was pinged
    `lost_rate`: the rate of packet loss
    `min`: the minimum (fastest) round trip ping request/reply
        time in milliseconds
    `avg`: the average round trip ping time in milliseconds
    `max`: the maximum (slowest) round trip ping time in
        milliseconds
  """
  if type(dest_ip) is not str:
    raise RepyArgumentError("Provided host must be a string!")

  if type(count) is not int:
    raise RepyArgumentError("Provided count must be an integer!")

  if type(timeout) is not int:
    raise RepyArgumentError("Provided timeout must be an integer!")

  # Check the input arguments (sanity)
  if not emulcomm._is_valid_ip_address(dest_ip):
    raise RepyArgumentError("Provided dest_ip is not valid! IP: '" + dest_ip + "'")

  if count < 1:
    raise RepyArgumentError("Provided count must be more than 0")

  if timeout < 1:
    raise RepyArgumentError("Provided timeout must be more than 0")

  result = []
  lost_count = 0

  # Account for the resources
  if emulcomm._is_loopback_ipaddr(dest_ip):
    nanny.tattle_quantity('loopsend', 256 * count)
    nanny.tattle_quantity('looprecv', 256 * count)
  else:
    nanny.tattle_quantity('netsend', 256 * count)
    nanny.tattle_quantity('netrecv', 256 * count)

  for i in xrange(count):
    delay = _do_one(dest_ip, timeout)
    if delay == None:
      lost_count +=1 
    else:
      delay = delay * 1000
      result.append(delay)

  if result:
    maxping = max(result)
    minping = min(result)
    avg = sum(result)/len(result)
    lost_rate = float(lost_count)/count*100.0
  else:
    maxping = None
    minping = None
    avg = None
    lost_rate = 100.0

  return {'max': maxping,'min': minping,'avg': avg, 'lost_rate': lost_rate, 'host': dest_ip}

##### Private functions ##### 
def _checksum(source_string):
  """
  <Purpose>
    A port of the functionality of in_cksum() from ping.c.
    It is part from http://github.com/samuel/python-ping.

  <Arguments>
    source_string: The data to calculate the checksum.

  <Returns>
    Returns the value of checksum computation.
  """
  sum = 0
  countTo = (len(source_string)/2)*2
  count = 0
  while count<countTo:
    thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
    sum = sum + thisVal
    sum = sum & 0xffffffff # Necessary?
    count = count + 2

  if countTo<len(source_string):
    sum = sum + ord(source_string[len(source_string) - 1])
    sum = sum & 0xffffffff # Necessary?

  sum = (sum >> 16)  +  (sum & 0xffff)
  sum = sum + (sum >> 16)
  answer = ~sum
  answer = answer & 0xffff

  # Swap bytes. Bugger me if I know why.
  answer = answer >> 8 | (answer << 8 & 0xff00)

  return answer

def _receive_one_ping(my_socket, ID, timeout):
  """
  <Purpose>
    Receive the ping from the socket.
    It is part from http://github.com/samuel/python-ping.

  <Arguments>
    my_socket: the address to communicate with.
    dest_addr: Time to wait for a response, in seconds.
    ID: a unique identifier in the ICMP ECHO REQUEST payload.

  <Returns>
    Returns either the delay (in seconds) or none.
  """
  timeLeft = timeout

  while True:
    startedSelect = time.time()
    whatReady = select.select([my_socket], [], [], timeLeft)
    howLongInSelect = (time.time() - startedSelect)
    if whatReady[0] == []: # Timeout
      return

    timeReceived = time.time()
    recPacket, addr = my_socket.recvfrom(1024)
    print len(recPacket)

    icmpHeader = recPacket[20:28]
    type, code, checksum, packetID, sequence = struct.unpack(
        "bbHHh", icmpHeader
    )
    # Filters out the echo request itself. 
    # This can be tested by pinging 127.0.0.1 
    # You'll see your own request
    if type != 8 and packetID == ID:
        bytesInDouble = struct.calcsize("d")
        timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
        return timeReceived - timeSent

  timeLeft = timeLeft - howLongInSelect
  if timeLeft <= 0:
    return

def _send_one_ping(my_socket, dest_addr, ID):
  """
  <Purpose>
    Send one ping to the given address.
    It is part from from http://github.com/samuel/python-ping.

  <Arguments>
    my_socket: the address to communicate with.
    dest_addr: Time to wait for a response, in seconds.
    ID: a unique identifier in the ICMP ECHO REQUEST payload.

  <Returns>
    None
  """
  ICMP_ECHO_REQUEST = 8
  dest_addr = socket.gethostbyname(dest_addr)

  # Header is type (8), code (8), checksum (16), id (16), sequence (16)
  my_checksum = 0

  # Make a dummy heder with a 0 checksum.
  header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
  bytesInDouble = struct.calcsize("d")
  data = (192 - bytesInDouble) * "Q"
  data = struct.pack("d", time.time()) + data

  # Calculate the checksum on the data and the dummy header.
  my_checksum = _checksum(header + data)

  # Now that we have the right checksum, we put that in. It's just easier
  # to make up a new header than to stuff it into the dummy.
  header = struct.pack(
    "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
  )
  packet = header + data
  my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1

def _do_one(dest_addr, timeout):
  """
  <Purpose>
    Returns either the delay (in seconds) or none on timeout.
    It is part from http://github.com/samuel/python-ping.

  <Arguments>
    dest_addr: the address to communicate with.
    timeout: Time to wait for a response, in seconds.

  <Returns>
    The result of delay (in seconds).
  """
  try:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP)
  except socket.error, (errno, msg):
    if errno == 1:
      # Operation not permitted
      msg = msg + (
        " - Note that ICMP messages can only be sent from processes"
        " running as root."
      )
      raise socket.error(msg)
    raise # raise the original error

  my_ID = os.getpid() & 0xFFFF

  _send_one_ping(my_socket, dest_addr, my_ID)
  delay = _receive_one_ping(my_socket, my_ID, timeout)
  my_socket.close()
  return delay
