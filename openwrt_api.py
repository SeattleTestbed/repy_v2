"""
   Author: Xuefeng Huang

   Start Date: 15 August 2015

   Description:

   This file provides a python interface to low-level system call or files 
   on the OpenWRT platform. It is designed to let researchers do a wide range 
   of network measurements on home gateway.
   
"""

import nanny

import socket

import portable_popen # Import for Popen

import textops # Import seattlelib's text processing lib

import re

import os # Provides some convenience functions

import emulcomm

# Get the exceptions
from exception_hierarchy import *

safe_open = open

##### Public Functions #####     
def get_network_bytes(interface):
  """
  <Purpose>
    Count the number of packets received and transmitted from an Interface.

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

  if os.path.exists("/proc/net/dev"):
    dev = safe_open("/proc/net/dev", "r")
    for line in dev:
      if interface in line:
        data = line.split('%s:' % interface)[1].split()
        rx_bytes, tx_bytes = (data[0], data[8])
        return {"recv": rx_bytes, "trans": tx_bytes}
  else:
    raise FileNotFoundError("Could not find /proc/net/dev!")

def get_network_packets(interface):
  """
  <Purpose>
    Count the number of packets received and transmitted from an interface

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

  if os.path.exists("/proc/net/dev"):
    dev = safe_open('/proc/net/dev', 'r')
    for line in dev:
      if interface in line:
        data = line.split('%s:' % interface)[1].split()
        rx_packets, tx_packets = (data[1], data[9])
        return {"recv": rx_packets, "trans": tx_packets}
  else:
    raise FileNotFoundError("Could not find /proc/net/dev!")

def get_network_interface():
  """
  <Purpose>
    Returns a list of available network interfaces.

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

def traceroute(dest_ip,port,max_hops,waittime,ttl):
  """
  <Purpose>
    Print the route packets take to network host 

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
    raise RepyArgumentError("Provided port is not valid! Port: "+str(port))

  if not emulcomm._is_allowed_localport("UDP", port):
    raise ResourceForbiddenError("Provided port is not allowed! Port: "+str(port))

  result = []

  # Infinite loop until reach destination or TTL reach maximum.
  while True:
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW,
      socket.IPPROTO_ICMP)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
      socket.IPPROTO_UDP)

    send_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    recv_sock.bind(("", port))
    bytesent = send_sock.sendto("", (dest_ip, port))

    # Account for the resources
    if _is_loopback_ipaddr(dest_ip):
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
    if curr_addr == dest_addr or ttl > max_hops:
      break

  return result

def ping(dest_ip,count):
  """
  <Purpose>
    Send ICMP ECHO_REQUEST to network hosts.

  <Arguments>
    dest_ip: the ip address to communicate with.
    count: Stop after sending count ECHO_REQUEST packets.

  <Exceptions>
    RepyArgumentError when the host name is not valid types
        or values

  <Side Effects>
    None

  <Returns>
    ping statistics as a dict, such as {'received': '2', 'jitter': '12.441', 
    'avgping': '27.302', 'minping': '14.861', 'host': 'www.google.com', 
    'maxping': '39.743', 'sent': '2'}
    `host`: the target hostname that was pinged
    `sent`: the number of ping request packets sent
    `received`: the number of ping reply packets received
    `minping`: the minimum (fastest) round trip ping request/reply
        time in milliseconds
    `avgping`: the average round trip ping time in milliseconds
    `maxping`: the maximum (slowest) round trip ping time in
        milliseconds
    `jitter`: the standard deviation between round trip ping times
        in milliseconds
  """
  if type(dest_ip) is not str:
    raise RepyArgumentError("Provided host must be a string!")

  if type(count) is not int:
    raise RepyArgumentError("Provided count must be an int!")

  # Check the input arguments (sanity)
  if not emulcomm._is_valid_ip_address(dest_ip):
    raise RepyArgumentError("Provided dest_ip is not valid! IP: '" + dest_ip + "'")

  if count < 1:
    raise RepyArgumentError("Provided count must be more than 0")

  process = portable_popen.Popen(['ping', '-c', str(count), dest_ip],)
  ping_output, err = process.communicate()
  return _parse(str(ping_output))

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

  iw_process = portable_popen.Popen(['iw', 'dev',interface, 'station','dump'])
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

  for i in range(len(station)):
    rules = {
      "station": station[i].strip(),
      "signal": signal[i].strip(),
      "signal_avg": signal_avg[i].strip(),
      "tx bitrate": tx_bitrate[i].strip(),
      "rx bitrate": rx_bitrate[i].strip(),
    }
    result.append(rules)
  
  return result

##### Private functions ##### 
def _get_match_groups(ping_output, regex):
  """
  <Purpose>
    Check whether it is ping output

  <Arguments>
    ping_output: the result to parse
    regex: the regular expression to match

  <Exceptions>
    None

  <Side Effects>
    None

  <Returns>
    Returns one or more subgroups of the match.
  """
  match = regex.search(ping_output)
  if not match:
    raise Exception('Invalid PING output:\n' + ping_output)
  return match.groups()

def _parse(ping_output):
  """
  <Purpose>
    Parses the `ping_output` string into a dictionary

  <Arguments>
    ping_output: the result to parse

  <Exceptions>
    None

  <Side Effects>
    None

  <Returns>
    ping statistics as a dict, such as {'received': '2', 'host': '173.194.123.19', 
    sent': '2'}
  """
  result = {}
  matcher = re.compile(r'PING ([a-zA-Z0-9.\-]+) \(')
  host = _get_match_groups(ping_output, matcher)[0]
  result['host'] = host
  matcher = re.compile(r'(\d+) packets transmitted, (\d+) packets received')
  sent, received = _get_match_groups(ping_output, matcher)
  result['sent'] = sent
  result['received'] = received

  return result