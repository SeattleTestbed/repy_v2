"""
   Author: Xuefeng Huang

   Start Date: 15 August 2015

   Description:

   This file provides a python interface to low-level system call or files 
   on the OpenWrt platform. It is designed to let researchers do a wide range 
   of network measurements on home gateway.
   
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
def get_network_bytes(interface):
  """
  <Purpose>
    Return the number of packets received and transmitted from an Interface.
    The information returned is looked up in the procfs.

  <Arguments>
    interface: the name of the interface to gather network information.

  <Exceptions>
    RepyArgumentError is raised if the interface aren't valid types or values
    FileNotFoundError is raised if the file does not exist

  <Side Effects>
    None

  <Returns>
    Network usage info as a dict such as {'trans': '59528148', 'recv': '1366399094'}
  """

  if type(interface) is not str:
    raise RepyArgumentError("get_network_bytes() takes a string as argument.")

  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")

  return {"recv": _get_interface_traffic_statistics(interface)['rx_bytes'],
    "trans": _get_interface_traffic_statistics(interface)['tx_bytes'],
    "rx_error": _get_interface_traffic_statistics(interface)['rx_error'],
    "tx_error": _get_interface_traffic_statistics(interface)['tx_error'],
    "rx_drop": _get_interface_traffic_statistics(interface)['rx_drop'],
    "tx_drop": _get_interface_traffic_statistics(interface)['tx_drop']}

def get_network_packets(interface):
  """
  <Purpose>
    Return the number of packets received and transmitted from an interface.
    The information returned is looked up in the procfs.

  <Arguments>
    interface: the name of the interface to gather network information.

  <Exceptions>
    RepyArgumentError is raised if the interface aren't valid types or values
    FileNotFoundError is raised if the file does not exist

  <Side Effects>
    None

  <Returns>
    Network usage info as a dict such as {'trans': '598602', 'recv': '1262217'}
  """
  if type(interface) is not str:
    raise RepyArgumentError("get_network_bytes() takes a string as argument.")
  
  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")

  return {"recv": _get_interface_traffic_statistics(interface)['rx_packets'],
    "trans": _get_interface_traffic_statistics(interface)['tx_packets'],
    "rx_error": _get_interface_traffic_statistics(interface)['rx_error'],
    "tx_error": _get_interface_traffic_statistics(interface)['tx_error'],
    "rx_drop": _get_interface_traffic_statistics(interface)['rx_drop'],
    "tx_drop": _get_interface_traffic_statistics(interface)['tx_drop']}

def get_network_interface():
  """
  <Purpose>
    Return a list of available network interfaces.

  <Arguments>
    None

  <Exceptions>
    FileNotFoundError is raised if the file does not exist

  <Side Effects>
    None

  <Returns>
    The list of strings(interface name).
  """
  if os.path.exists("/proc/net/dev"):
    dev = safe_open("/proc/net/dev", "r").readlines()
    header_line = dev[1]
    header_names = header_line[header_line.index("|")+1:].replace("|", " ").split()

    result = []
    for line in dev[2:]:
      interface = line[:line.index(":")].strip()
      result.append(interface)
    return result
  else:
    raise FileNotFoundError("Could not find /proc/net/dev!")

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
    This operation consumes 28 bytes + number of bytes of the message that
    were transmitted. This requires that the localport is allowed.

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
    raise RepyArgumentError("Provided port is not valid! Port: " + str(port) + "'")

  if max_hops > 255:
    raise RepyArgumentError("Provided max_hops: " + str(max_hops) + " is larger than 255.'")

  result = []

  # Infinite loop until reach destination or TTL reach maximum.
  while True:
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
      socket.IPPROTO_ICMP)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
      socket.IPPROTO_UDP)

    send_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    recv_sock.bind(("", port))
    bytessent = send_sock.sendto("", (dest_ip, port))

    # Account for the resources
    if emulcomm._is_loopback_ipaddr(dest_ip):
      nanny.tattle_quantity('loopsend', bytessent + 28)
    else:
      nanny.tattle_quantity('netsend', bytessent + 28)

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

  for i in xrange(count):
    delay = _do_one(dest_ip, timeout)

    if delay  ==  None:
      lost_count +=1 
    else:
      delay  =  delay * 1000
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

def get_station(interface):
  """
   <Purpose>
      To get station statistic information such as the amount of tx/rx bytes, the 
      last TX bitrate (including MCS rate) you can do

   <Arguments>
      interface: the name of the interface to gather network information.

   <Exceptions>
      RepyArgumentError is raised if the argument isn't valid types or values

   <Side Effects>
      None

   <Returns>
     station statistic informatio as a dict such as {{'signal': '-77 [-78, -83] dBm', 
    'station': '54:4e:90:06:f3:6f', 'tx bitrate': '57.8 MBit/s MCS 5 short GI', 'rx 
    bitrate': '1.0 MBit/s', 'signal_avg': '-88 [-90, -92] dBm'}, {'signal': '-40 [-42, 
    -44] dBm', 'station': 'ac:81:12:53:8e:0f', 'tx bitrate': '65.0 MBit/s MCS 6 short 
    GI', 'rx bitrate': '18.0 MBit/s', 'signal_avg': '-42 [-44, -48] dBm'}}

  """
  if type(interface) is not str:
    raise RepyArgumentError("get_station() takes a string as argument.")

  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")
  try:
    iw_process = portable_popen.Popen(['iw', 'dev',interface, 'station','dump'])
  except:
    raise FileNotFoundError('iw: command not found')
    
  iw_output, _ = iw_process.communicate()
  iw_lines = textops.textops_rawtexttolines(iw_output)

  station = textops.textops_grep("Station", iw_lines)
  station = textops.textops_cut(station, delimiter=" ", fields=[1])

  signal = textops.textops_grep("signal:", iw_lines)
  signal = textops.textops_cut(signal, delimiter=":", fields=[1])         

  signal_avg = textops.textops_grep("signal avg:", iw_lines)
  signal_avg = textops.textops_cut(signal_avg, delimiter=":", fields=[1])         

  tx_bitrate = textops.textops_grep("tx bitrate:", iw_lines)
  tx_bitrate = textops.textops_cut(tx_bitrate, delimiter=":", fields=[1])         

  rx_bitrate = textops.textops_grep("rx bitrate:", iw_lines)
  rx_bitrate = textops.textops_cut(rx_bitrate, delimiter=":", fields=[1])         

  result = []

  for st, sig, sig_avg, tx, rx in zip(station, signal, signal_avg, tx_bitrate, rx_bitrate):
    rules = {
      "station": st.strip(),
      "signal": sig.strip(),
      "signal_avg": sig_avg.strip(),
      "tx bitrate": tx.strip(),
      "rx bitrate": rx.strip(),
    }
    result.append(rules)
  
  return result

##### Private functions ##### 
def _get_interface_traffic_statistics(interface):
  """
  <Purpose>
    Return traffic statistics from an Interface. The information returned is 
    looked up in the procfs.

  <Arguments>
    interface: the name of the interface to gather network information.

  <Returns>
    Network usage info as a dict such as {'rx_bytes': '59528148', 'tx_bytes': '1366399094', 
    'tx_packets': '598602', 'rx_packets': '1262217'}
  """
  if os.path.exists("/proc/net/dev"):
    dev = safe_open('/proc/net/dev', 'r')
    for line in dev:
      if interface in line:
        data = line.split('%s:' % interface)[1].split()
        rx_packets, tx_packets = (data[1], data[9])
        rx_bytes, tx_bytes = (data[0], data[8])
        rx_error, tx_error = (data[2], data[10])
        rx_drop, tx_drop = (data[3], data[11])
        return {'rx_packets': rx_packets, 'tx_packets': tx_packets, 'rx_bytes': rx_bytes, 'tx_bytes': tx_bytes,
        'rx_error': rx_error, 'tx_error': tx_error, 'rx_drop': rx_drop, 'tx_drop': tx_drop}
  else:
    raise FileNotFoundError("Could not find /proc/net/dev!")

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

  dest_addr  =  socket.gethostbyname(dest_addr)

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
  icmp = socket.getprotobyname("icmp")
  try:
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
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