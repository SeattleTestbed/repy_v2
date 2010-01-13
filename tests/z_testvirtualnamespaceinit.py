"""
Author: Armon Dadgar
Description:
  This test tries to initialize a VirtualNamespace and checks that it
  behaves as expected.
"""

if callfunc == "initialize":
  # Small code snippet, safe
  safe_code = "meaning_of_life = 42\n"

  # Unsafe snippet
  unsafe_code = "import sys\n"

  # Try to make the safe virtual namespace
  safe_virt = VirtualNamespace(safe_code)

  # Try to make the un-safe virtual namespace
  try:
    unsafe_virt = VirtualNamespace(unsafe_code)
    print "Error! Created unsafe virtual namespace!"
  except ValueError:
    pass # We expect a safety error

  # Try to initialize with a name
  safe_virt_2 = VirtualNamespace(safe_code, "Hitchhikers Guide")

  # Try some bogus code
  try:
    junk = VirtualNamespace(123)
    print "Error! Created junk namespace!"
  except TypeError:
    pass # This is expected

  try:
    junk = VirtualNamespace(safe_code, 123)
    print "Error! Junk name accepted!"
  except TypeError:
    pass # This is expected

