# See RFC 2030 (http://www.ietf.org/rfc/rfc2030.txt) for details about NTP

# this unpacks the data from the packet and changes it to a float
def convert_timestamp_to_float(timestamp):
  integerpart = (ord(timestamp[0])<<24) + (ord(timestamp[1])<<16) + (ord(timestamp[2])<<8) + (ord(timestamp[3]))
  floatpart = (ord(timestamp[4])<<24) + (ord(timestamp[5])<<16) + (ord(timestamp[6])<<8) + (ord(timestamp[7]))
  return integerpart + floatpart / float(2**32)

def decode_NTP_packet(ip, port, mess, ch):
  print "From "+str(ip)+":"+str(port)+", I received NTP data."
  print "NTP Reference Identifier:",mess[12:16]
  print "NTP Transmit Time (in seconds since Jan 1st, 1900):", convert_timestamp_to_float(mess[40:48]) 
  stopcomm(ch)

if callfunc == 'initialize':
  ip = getmyip()
  timeservers = ["time-a.nist.gov", "time-b.nist.gov", "time-a.timefreq.bldrdoc.gov", "time-b.timefreq.bldrdoc.gov", "time-c.timefreq.bldrdoc.gov", "utcnist.colorado.edu", "time.nist.gov", "time-nw.nist.gov", "nist1.symmetricom.com", "nist1-dc.WiTime.net", "nist1-ny.WiTime.net", "nist1-sj.WiTime.net", "nist1.aol-ca.symmetricom.com", "nist1.aol-va.symmetricom.com", "nist1.columbiacountyga.gov", "nist.expertsmi.com", "nist.netservicesgroup.com"]

  # choose a random time server
  servername = timeservers[int(randomfloat()*len(timeservers))]

  print "Using: ", servername
  # this sends a request, version 3 in "client mode"
  ntp_request_string = chr(27)+chr(0)*47
  recvmess(ip,12345, decode_NTP_packet)
  sendmess(servername,123, ntp_request_string, ip, 12345) # 123 is the NTP port
