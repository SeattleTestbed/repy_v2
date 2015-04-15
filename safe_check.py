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

if __name__ == "__main__":
  # Get the user "code"
  usercode = sys.stdin.read()
  
  # Output buffer
  output = ""
  
  # Check the code
  try:
    value = safe.safe_check(usercode)
    output += str(value)
  except Exception,e:
    # To address issue #95, we need to subtract 2 from the line number.
    # This compensates for adding the encoding information at the top of the
    # file.
    try:
      e.lineno = e.lineno - 2
    except AttributeError:
      # Some exceptions may not have line numbers.  If so, ignore
      pass
    output += str(type(e)) + " " + str(e)
  
  # Write out
  sys.stdout.write(output)
  sys.stdout.flush()
  
