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
import encoding_header



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
    # Adjust traceback line numbers, see SeattleTestbed/repy_v2#95.
    try:
      e.lineno = e.lineno - \
          len(encoding_header.ENCODING_DECLARATION.splitlines())
    except (TypeError, AttributeError):
      # Ignore exceptions with line numbers that are non-numeric (i.e.
      # `None`), or have no `lineno` attribute altogether.
      pass
    output += str(type(e)) + " " + str(e)
  
  # Write out
  sys.stdout.write(output)
  sys.stdout.flush()
  
