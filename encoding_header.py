"""
<Program Name>
  encoding_header.py

<Purpose>
  This mini module provides the ENCODING_DECLARATION constant, a string that is
  prepended to code loaded into VirtualNamespace objects. This is prepended to
  such code in order to specify UTF-8 encoding and prevent certain bugs.

  Because prepending it to code results in distortions in reported line numbers
  in tracebacks when exceptions occur, this constant is imported in files that
  would raise such exceptions, so as to subtract the number of lines it
  contains from reported line numbers.

  While it may seem silly to have a module for a single constant, multiple
  modules import this, and because they also depend on each other, it was
  decided to keep this in its own separate module in order to help avoid import
  loops. In time, we may find more such things to pull together.
  
  As of this writing, it is used by:
    virtual_namespace.py
    tracebackrepy.py
    safe_check.py
    safe.py

  For history relevant to the above, see SeattleTestbed/repy_v2#95 and #96.

"""

# Treat any user code as having UTF-8 encoding. For this, 
# prepend this encoding string
ENCODING_DECLARATION = "# coding: utf-8\n\n"
