"""
Author: Armon Dadgar
Description:
  This test tries to initialize various key/value pairs in the global
  _context dictionary, and checks that no non-safe keys are allowed.
"""

# Tries to set an unsafe key
def try_key(key):
  try:
    _context[key] = True
  except ValueError:
    pass
  except TypeError:
    pass
  else:
    raise Exception, "Unsafe key '"+key+"' allowed!"


if callfunc == "initialize":
  # Try a bunch of keys
  try_key("__builtins__")
  try_key("__metaclass__")
  try_key(123)
  try_key(42L)
  try_key(3.1415)
  try_key("func_code")
  try_key("__")

  # These keys should be allowed
  _context["test"] = True
  _context["allowed"] = True
  _context["with_underscore"] = True
  _context["__init__"] = True


