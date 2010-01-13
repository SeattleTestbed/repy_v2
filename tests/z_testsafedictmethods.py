"""
Author: Armon Dadgar
Description:
  Tries many of the common operations on a SafeDict to make sure they work.
"""

if callfunc == "initialize":
  # Get a normal dict
  norm = {}
  norm["hi"] = 123
  norm["test"] = "person"
  norm["blahblah"] = 123

  # Get the SafeDict with the same entries
  d = SafeDict(norm)

  keys = d.keys()
  if "hi" not in keys or "test" not in keys or "blahblah" not in keys:
    raise Exception, "SafeDict is missing some keys! Keys: "+str(keys)

  # Copy the dictionary
  d_copy1 = d.copy()
  d_copy2 = SafeDict(d)

  # Check equality
  if not d == d_copy1:
    raise Exception, "Copy 1 is not the same!"

  if not d == d_copy2:
    raise Exception, "Copy 2 is not the same!"

  # Check that I cannot modify the dictionary
  try:
    d.foo = None
  except TypeError:
    pass

  try:
    del d.copy
  except TypeError:
    pass
  

