"""
   Author: Justin Cappos

   Start Date: 19 July 2008

   Description:
   
   Provides a unique ID when requested...
"""

import threading        # to get the current thread name to prevent a race


# this dictionary contains keys that are thread names and values that are 
# integers.   The value starts at 0 and is incremented every time we give 
# out an ID.   The ID is formed from those two parts (thread name and ID)
usedids = {}

def getuniqueid():
  """
   <Purpose>
      Provides a unique identifier.

   <Arguments>
      None

   <Exceptions>
      None.

   <Side Effects>
      None.

   <Returns>
      The identifier (the string)
  """

  # NOTE: I make the assumption that threads have unique names.   I toyed with 
  # the thought of using the id (memory location) of the thread object, but I
  # was unsure this would behave well if dummy threads exist or if gc happens
  # in the middle of this function, etc.
  myname = threading.currentThread().getName()
  if myname not in usedids:
    usedids[myname] = 0

  usedids[myname] = usedids[myname]+1
  return myname + ":"+str(usedids[myname])
