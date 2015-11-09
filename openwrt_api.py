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

  <Resource Consumption>
    Consumes 4K of procfsread.

  <Returns>
    Network usage info as a dict such as {'trans': '59528148', 'recv': '1366399094', 'rx_error': '0',
    'tx_error': '0', 'rx_drop': '0', 'tx_drop': 0}
  """

  if type(interface) is not str:
    raise RepyArgumentError("get_network_bytes() takes a string as argument.")

  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")

  nanny.tattle_quantity('procfsread', 4096)

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

  <Resource Consumption>
    Consumes 4K of procfsread.

  <Returns>
    Network usage info as a dict such as {'trans': '598602', 'recv': '1262217', 'rx_error': '0',
    'tx_error': '0', 'rx_drop': '0', 'tx_drop': 0}
  """
  if type(interface) is not str:
    raise RepyArgumentError("get_network_bytes() takes a string as argument.")
  
  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")

  nanny.tattle_quantity('procfsread', 4096)

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

  <Resource Consumption>
    Consumes 4K of procfsread.

  <Returns>
    The list of strings(interface name).
  """
  nanny.tattle_quantity('procfsread', 4096)
  
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

def get_station(interface):
  """
   <Purpose>
      To get station statistic information such as the amount of tx/rx bytes, the 
      last TX bitrate (including MCS rate) you can do

   <Arguments>
      interface: the name of the interface to gather network information.

   <Exceptions>
      RepyArgumentError is raised if the argument isn't valid types or values.
      FileNotFoundError is raised if iw tool does not exist.

   <Side Effects>
      None

   <Returns>
     station statistic informatio as a dict such as [{'signal': '-77 [-78, -83] dBm', 
    'station': '54:4e:90:06:f3:6f', 'tx bitrate': '57.8 MBit/s MCS 5 short GI', 'rx 
    bitrate': '1.0 MBit/s', 'signal_avg': '-88 [-90, -92] dBm'}, {'signal': '-40 [-42, 
    -44] dBm', 'station': 'ac:81:12:53:8e:0f', 'tx bitrate': '65.0 MBit/s MCS 6 short 
    GI', 'rx bitrate': '18.0 MBit/s', 'signal_avg': '-42 [-44, -48] dBm'}]

  """
  if type(interface) is not str:
    raise RepyArgumentError("get_station() takes a string as argument.")

  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")
  try:
    iw_process = portable_popen.Popen(['iw', 'dev', interface, 'station','dump'])
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

  tx_packets = textops.textops_grep("tx packets:", iw_lines)
  tx_packets = textops.textops_cut(tx_packets, delimiter=":", fields=[1])         

  rx_packets = textops.textops_grep("rx packets:", iw_lines)
  rx_packets = textops.textops_cut(rx_packets, delimiter=":", fields=[1]) 

  rx_bytes = textops.textops_grep("rx bytes:", iw_lines)
  rx_bytes = textops.textops_cut(rx_bytes, delimiter=":", fields=[1])

  tx_bytes = textops.textops_grep("tx bytes:", iw_lines)
  tx_bytes = textops.textops_cut(tx_bytes, delimiter=":", fields=[1])

  tx_retries = textops.textops_grep("tx retries:", iw_lines)
  tx_retries = textops.textops_cut(tx_retries, delimiter=":", fields=[1])

  tx_failed = textops.textops_grep("tx failed:", iw_lines)
  tx_failed  = textops.textops_cut(tx_failed , delimiter=":", fields=[1])        

  result = []

  for i in range(len(station)):
    rules = {
      "station": station[i].strip(),
      "signal": signal[i].strip(),
      "signal_avg": signal_avg[i].strip(),
      "tx packets": tx_packets[i].strip(),
      "rx packets": rx_packets[i].strip(),
      "tx bytes": tx_bytes[i].strip(),
      "rx bytes": rx_bytes[i].strip(),
      "tx retries": tx_retries[i].strip(),
      "tx failed": tx_failed[i].strip(),            
    }
    result.append(rules)
  
  return result

def scan(interface):
  """
  <Purpose>
    Collect a list of access points found with one WiFi. For each access point 
    we collect BSSID, SSID ,signal strength and channel.

  <Arguments>
    interface: the name of the interface to gather network information.

  <Exceptions>
    FileNotFoundError is raised if iw tool does not exist.

  <Side Effects>
    None

  <Returns>
    A list of access points such as[{'BSSID': 2c:3e:cf:a0:23:51, 'SSID': nyu,
    'signal': -78.00 dBm, 'Channel': 11}]

  """
  if type(interface) is not str:
    raise RepyArgumentError("scan() takes a string as argument.")

  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")
  try:
    iw_process = portable_popen.Popen(['iw', 'dev', interface, 'scan'])
  except:
    raise FileNotFoundError('iw: command not found')
    
  iw_output, _ = iw_process.communicate()
  iw_lines = textops.textops_rawtexttolines(iw_output)

  BSSID = textops.textops_grep("BSS", iw_lines)
  BSSID = textops.textops_cut(BSSID, delimiter=" ", fields=[1])

  signal = textops.textops_grep("signal:", iw_lines)
  signal = textops.textops_cut(signal, delimiter=":", fields=[1])         

  SSID = textops.textops_grep("SSID", iw_lines)
  SSID = textops.textops_cut(SSID, delimiter=":", fields=[1])

  channel = textops.textops_grep("primary channel", iw_lines)
  channel = textops.textops_cut(channel, delimiter=":", fields=[1])                 

  result = []

  for bbs, sig, ssid, chan in zip(BSSID, signal, SSID, channel):
    rules = {
      "BSSID": bbs.strip(),
      "Signal": sig.strip(),
      "SSID": ssid.strip(),
      "channel": chan.strip(),
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

  <Exceptions>
    FileNotFoundError is raised if the file does not exist

  <Returns>
    Network usage info as a dict such as {'rx_bytes': '59528148', 'tx_bytes': '1366399094', 
    'tx_packets': '598602', 'rx_packets': '1262217'}
  """
  #cat /proc/net/dev 
  #Inter-|   Receive                                                |  Transmit
  #face |bytes    packets errs drop fifo frame compressed multicast|bytes    packets errs drop fifo colls carrier compressed
  #eth0: 1414039694 1492858    0    0    0     0          0         0 78372019  827138    0    0    0     0       0          0
  #  lo: 5071019   36780    0    0    0     0          0         0  5071019   36780    0    0    0     0       0          0

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
