"""
<Program Name>
  testportfiller.py
  
<Started>
  November 13, 2008
  
<Author>
  Brent Couvrette
  
<Purpose>
  This module is used to fill in the port numbers in the repy unit tests.
  Because the unit tests can be run on any random node you have access to,
  hardcoding in a port or even a small set of ports is asking for failure
  when the tests are run on a node that does not have those ports open.
  Therefore it is best to dynamically determine what ports are available on
  the node that is being used, then make all the tests use those ports.  
  However, we also want to be able to still run the unit tests locally, which
  requires that this functionallity be in two places, hence the existence of
  this module.
  
  If run on its own, this module will find and replace all of the uses of port
  numbers in the repy tests with some default port.
  
  If included, the replacePorts function should be called to replace all the
  ports with the given port numbers (more details in the replacePorts doc).
"""

import glob


# Goes through all of the test files and replaces the <messport> and <connport>
# tags with the ports that were found on the actual vessel
def replace_ports(foundMessports, foundConnports):
  """
  <Purpose>
    Replaces all mess and conn port tags in the repy test files with the given
    lists of mess and conn ports.  Currently, to completely replace every port,
    foundMessports and foundConnports must be of length at least 3.  However,
    if they are shorter, It will still replace as many as it can, though this
    will leave some tests with invalid syntax as they still have some 
    unreplaced tags.
    
  <Arguments>
    foundMessports:
        The list of port numbers that should be used to replace the <messport>
        tags as shown:
          <messport>  =>  foundMessports[0]
          <messport1> =>  foundMessports[1]
          <messport2> =>  foundMessports[2]
        If a foundMessports index as given above does not exist, then that tag
        will just not get replaced.
        
    foundConnports:
        The list of port numbers that should be used to replace the <connport>
        tags as shown:
          <connport>  =>  foundConnports[0]
          <connport1> =>  foundConnports[1]
          <connport2> =>  foundConnports[2]
        If a foundConnports index as given above does not exist, then that tag
        will just not get replaced.
        
  <Side Effects>
    Changes all of the repy unit tests to include actual port numbers as 
    possible.
    
  <Returns>
    None.
  """
  for testfile in glob.glob("rs_*.py") + glob.glob("rn_*.py") + \
      glob.glob("rz_*.py") + glob.glob("rb_*.py") + glob.glob("ru_*.py") + \
      glob.glob("re_*.py") + glob.glob("rl_*.py") +glob.glob("s_*.py") + \
      glob.glob("n_*.py") + glob.glob("z_*.py") + glob.glob("b_*.py") + \
      glob.glob("u_*.py") + glob.glob("e_*.py") + glob.glob("l_*.py") + \
      glob.glob("ut_*.repy") + glob.glob("ut_*.r2py") + \
      glob.glob('restrictions.*'):
    # read in the initial file
    inFile = file(testfile, 'r')
    filestring = inFile.read()
    inFile.close()

    # MMM: We probably need a better way of doing this then just if
    # statements if we want to expand this in the future.
    # Replace the instances of messport that we can replace
    if len(foundMessports) >= 1:
      filestring = filestring.replace('<messport>', foundMessports[0])
    if len(foundMessports) >= 2:
      filestring = filestring.replace('<messport1>', foundMessports[1])
    if len(foundMessports) >= 3:
      filestring = filestring.replace('<messport2>', foundMessports[2])
    if len(foundMessports) >= 4:
      filestring = filestring.replace('<messport3>', foundMessports[3])
    if len(foundMessports) >= 5:
      filestring = filestring.replace('<messport4>', foundMessports[4])

    # Replace the instances of connport that we can replace
    if len(foundConnports) >= 1:
      filestring = filestring.replace('<connport>', foundConnports[0])
    if len(foundConnports) >= 2:
      filestring = filestring.replace('<connport1>', foundConnports[1])
    if len(foundConnports) >= 3:
      filestring = filestring.replace('<connport2>', foundConnports[2])
    if len(foundConnports) >= 4:
      filestring = filestring.replace('<connport3>', foundConnports[3])
    if len(foundConnports) >= 5:
      filestring = filestring.replace('<connport4>', foundConnports[4])
				
    # write out the file with our changes
    outFile = file(testfile, 'w')
    outFile.write(filestring)
    outFile.close()
      

def main():
  # If running separately, just put back in the values that were previously
  # hardcoded.
  replace_ports(['12345', '12346', '12347'], ['12345', '12346', '12347'])
  
if __name__ == '__main__':
  main()
