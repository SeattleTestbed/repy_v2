"""
Author: Armon Dadgar
Description:
  This test tries to initialize a VirtualNamespace and checks that it
  behaves as expected.
"""

# Small code snippet, safe
safe_code = "meaning_of_life = 42\n"

# Unsafe snippet
unsafe_code = "import sys\n"

# Try to make the safe virtual namespace
safe_virt = createvirtualnamespace(safe_code, "TEST VN")

# Try to make the un-safe virtual namespace
try:
  unsafe_virt = createvirtualnamespace(unsafe_code, "TEST VN 2")
  print "Error! Created unsafe virtual namespace!"
except CodeUnsafeError:
  pass # We expect a safety error

# Try some bogus code
try:
  junk = createvirtualnamespace(123, "TEST VN 3")
  print "Error! Created junk namespace!"
except RepyArgumentError:
  pass # This is expected

try:
  junk = createvirtualnamespace(safe_code, 123)
  print "Error! Junk name accepted!"
except RepyArgumentError:
  pass # This is expected

