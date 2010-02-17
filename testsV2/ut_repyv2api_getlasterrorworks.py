"""
This unit test tests that getlasterror behaves in a sane manner.
We check:
  1) Output with no exception
  2) Output with a ZeroDivisionError
  3) Output with an exception on another stack frame
  4) Output after an exception has been handled
"""

#pragma repy

# To to call the function when there is no error
debug_str = getlasterror()

# We should get None
if debug_str is not None:
  print "Got a debug string without an exception! Got: "+debug_str

# Try to do something and get the debug string
try:
  v = 5 / 0
except:
  debug_str = getlasterror()
  if debug_str is None or len(debug_str) < 100:
    print "Did not get a debug_str or too short! Got: "+str(debug_str)
else:
  print "Error! Failed to get an exception (1)"

# Declare a function which raises an exception
def badfunc():
  raise Exception, "Error!"

# Test that we can find that stack entry in the debug string
try:
  badfunc()
except:
  debug_str = getlasterror()
  if "badfunc" not in debug_str:
    print "Did not find stack entry for 'badfunc' in the debug string! Got: "+debug_str
else:
    print "Error! Failed to get an exception (2)"


# We should try to check that getlasterror() does not return the same string
# from the last exception
debug_str_2 = getlasterror()

if debug_str_2 is not None:
  print "Did not get None, after exception was handled! Got: "+debug_str_2
  print "Previous debug str: "+debug_str


