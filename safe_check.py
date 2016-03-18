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
# code. This ENCODING_DECLARATION is imported from mini module encoding_header.
# It has the effect of treating user code as having UTF-8 encoding, preventing
# certain bugs. As a side effect, prepending this header to code also results
# in traceback line numbers being off. To remedy this, we import the code
# header in several modules so as to subtract the number of lines it contains
# from such line counts. We place it in its own file so that it can be imported
# by multiple files with interdependencies, to avoid import loops.
# For more info, see SeattleTestbed/repy_v2#95 and #96.
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
    # In virtual_namespace.py, we prepend an encoding declaration to 
    # each user file we read in.
    # Now, we need to subtract the number of lines consumed by the 
    # encoding declaration from the current exception's line number 
    # so that the line number we output corresponds with the actual 
    # user code again (see SeattleTestbed/repy_v2#95).
    try:
      e.lineno = e.lineno - \
                 len(encoding_header.ENCODING_DECLARATION.splitlines())
    except AttributeError:
      # Some exceptions may not have line numbers.  If so, ignore
      pass
    output += str(type(e)) + " " + str(e)
  
  # Write out
  sys.stdout.write(output)
  sys.stdout.flush()
  
