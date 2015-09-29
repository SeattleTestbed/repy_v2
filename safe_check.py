"""
Author: Armon Dadgar
Date: June 11th, 2009
Description:
  This simple script reads "code" from stdin, and runs safe.safe_check() on it.
  The resulting return value or exception is serialized and written to stdout.
  The purpose of this script is to be called from the main repy.py script so that the
  memory used by the safe.safe_check() will be reclaimed when this process quits.

"""

import safe
import sys

# virtual_namespace prepends a multiline ENCODING_DECLARATION to user 
# code. We import it to adjust traceback line numbers accordingly 
# (see SeattleTestbed/repy_v2#95).
import virtual_namespace



if __name__ == "__main__":
  # Get the user "code"
  usercode = sys.stdin.read()
  
  # Output buffer
  output = ""
  
  # Check the code
  try:
    value = safe.safe_check(usercode)
    output += str(value)
  except Exception, e:
    # In virtual_namespace.py, we prepend an encoding declaration to 
    # each user file we read in.
    # Now, we need to subtract the number of lines consumed by the 
    # encoding declaration from the current exception's line number 
    # so that the line number we output corresponds with the actual 
    # user code again (see SeattleTestbed/repy_v2#95).
    try:
      e.lineno = e.lineno - len(virtual_namespace.ENCODING_DECLARATION.splitlines())
    except AttributeError:
      # Some exceptions may not have line numbers.  If so, ignore
      pass
    output += str(type(e)) + " " + str(e)
  
  # Write out
  sys.stdout.write(output)
  sys.stdout.flush()
  
