"""
Author: Armon Dadgar
Description:
  This test tries to initialize various key/value pairs in the SafeDict
  object, and checks that no non-safe keys are allowed.
"""

# Tries to set an unsafe key
def try_key(d,key):
  try:
    d[key] = True
  except ValueError:
    pass
  except TypeError:
    pass
  else:
    raise Exception, "Unsafe key '"+key+"' allowed!"


if callfunc == "initialize":
  # Get the dict
  d = SafeDict()

  # Try a bunch of keys
  try_key(d, "__builtins__")
  try_key(d, "__metaclass__")
  try_key(d, 123)
  try_key(d, 42L)
  try_key(d, 3.1415)
  try_key(d, "func_code")
  try_key(d, "__")

  # These keys should be allowed
  d["test"] = True
  d["allowed"] = True
  d["with_underscore"] = True
  d["__init__"] = True

  # Create an unsafe dictionary
  unsafe = {"__builtins__":{},"__metaclass__":None,123:234}

  # Try to make this a SafeDict
  try:
    bad = SafeDict(unsafe)
  except ValueError:
    pass
  except TypeError:
    pass

  
