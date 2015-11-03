"""
  Author: Xuefeng Huang

  Start Date: 30 October 2015

  Description:

  This file provides a python interface to low-level system call  
  on OS X. It is designed to let researchers do a wide range 
  of network measurements on home gateway.
   
"""
import subprocess

# Get the exceptions
from exception_hierarchy import *


def get_network_bytes(interface):
  """
  <Purpose>
    Return the number of packets received and transmitted from an Interface.
    The information returned is parsed the result of netstat.

  <Arguments>
    interface: the name of the interface to gather network information.

  <Exceptions>
    RepyArgumentError is raised if the interface aren't valid types or values
    FileNotFoundError is raised if the file does not exist

  <Side Effects>
    None

  <Returns>
    Network usage info as a dict such as {'Ierrs': '0', 'Oerrs': '0', 'Obytes':
     '6265721', 'Ibytes': '6265721', 'Network': '<Link#1>'}
  """

  if type(interface) is not str:
    raise RepyArgumentError("get_network_bytes() takes a string as argument.")

  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")

  result = []

  for i in range(len(_get_interface_traffic_statistics(interface))):
    result.append({"Network": _get_interface_traffic_statistics(interface)[i]['Network'],
    "Ibytes": _get_interface_traffic_statistics(interface)[i]['Ibytes'],
    "Obytes": _get_interface_traffic_statistics(interface)[i]['Obytes'],
    "Ierrs": _get_interface_traffic_statistics(interface)[i]['Ierrs'],
    "Oerrs": _get_interface_traffic_statistics(interface)[i]['Oerrs']})

  return result

def get_network_packets(interface):
  """
  <Purpose>
    Return the number of packets received and transmitted from an interface.
    The information returned is parsed the result of netstat.

  <Arguments>
    interface: the name of the interface to gather network information.

  <Exceptions>
    RepyArgumentError is raised if the interface aren't valid types or values
    FileNotFoundError is raised if the file does not exist

  <Side Effects>
    None

  <Returns>
    Network usage info as a dict such as {'Ipkts': '33643', 'Ierrs': '0', 'Oerrs':
     '0', 'Network': '<Link#1>', 'Opkts': '33643'}
  """
  if type(interface) is not str:
    raise RepyArgumentError("get_network_bytes() takes a string as argument.")
  
  # Check the input arguments (sanity)
  if interface not in get_network_interface():
    raise RepyArgumentError("interface "+ interface + " is not available.")

  result = []

  for i in range(len(_get_interface_traffic_statistics(interface))):
    result.append({"Network": _get_interface_traffic_statistics(interface)[i]['Network'],
    "Ipkts": _get_interface_traffic_statistics(interface)[i]['Ipkts'],
    "Opkts": _get_interface_traffic_statistics(interface)[i]['Opkts'],
    "Ierrs": _get_interface_traffic_statistics(interface)[i]['Ierrs'],
    "Oerrs": _get_interface_traffic_statistics(interface)[i]['Oerrs']})

  return result

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
    The list of strings(interface name). Such as ['lo0', 'gif0*', 'stf0*', 
    'en0', 'en1', 'en2', 'p2p0', 'awdl0', 'bridg']
  """  
  process = subprocess.Popen(['netstat', '-b', '-i', 'en1'], stdout = subprocess.PIPE)
  netstat = process.stdout
  result = []

  for line in netstat:
    result.append(line.split())

  interfaceList = []

  for i in range(1,len(result)):
    if result[i][0] not in interfaceList :
      interfaceList .append(result[i][0])

  return interfaceList 
      
##### Private functions ##### 
def _get_interface_traffic_statistics(interface):
  """
  <Purpose>
    Return traffic statistics from an Interface. The information returned is 
    parsed the result of netstat.

  <Arguments>
    interface: the name of the interface to gather network information.

  <Exceptions>
    FileNotFoundError is raised if the file does not exist

  <Returns>
    Network usage info as a dict such as {'rx_bytes': '59528148', 'tx_bytes': '1366399094', 
    'tx_packets': '598602', 'rx_packets': '1262217'}
  """
  process = subprocess.Popen(['netstat', '-b', '-i', 'en1'], stdout = subprocess.PIPE)
  netstat = process.stdout
  result_include_addr = []
  result_not_include_addr = []
#$ netstat -b -i en1
#Name  Mtu   Network       Address            Ipkts Ierrs     Ibytes    Opkts Oerrs     Obytes  Coll
#lo0   16384 <Link#1>                         33616     0    6262436    33616     0    6262436     0
#lo0   16384 localhost   ::1                  33616     -    6262436    33616     -    6262436     -
#lo0   16384 127           localhost          33616     -    6262436    33616     -    6262436     -
#lo0   16384 fe80::1%lo0 fe80:1::1            33616     -    6262436    33616     -    6262436     -
  for line in netstat:
    if len(line.split()) == 11:
      result_include_addr.append(line.split())
    if len(line.split()) == 10:
      result_not_include_addr.append(line.split()) 
  
  statistics = []
# There are two formates of netstat result, one is include address and another
# one is not, so we need to store statistics via two ways.
  for i in range(len(result_include_addr)):
    if result_include_addr[i][0] == interface:
      statistics.append({'Name':result_include_addr[i][0],'Network': result_include_addr[i][2],
      'Ipkts':result_include_addr[i][4], 'Ierrs':result_include_addr[i][5],'Ibytes': 
      result_include_addr[i][6], 'Opkts': result_include_addr[i][7], 'Oerrs': result_include_addr[i][8], 
      'Obytes': result_include_addr[i][9]})

  for i in range(len(result_not_include_addr)):
    if result_not_include_addr[i][0] == interface:
      statistics.append({'Name':result_not_include_addr[i][0],'Network': result_not_include_addr[i][2],
      'Ipkts':result_not_include_addr[i][3], 'Ierrs':result_not_include_addr[i][4],'Ibytes': 
      result_not_include_addr[i][5], 'Opkts': result_not_include_addr[i][6], 'Oerrs': result_not_include_addr[i][7], 
      'Obytes': result_not_include_addr[i][8]})

  return statistics
