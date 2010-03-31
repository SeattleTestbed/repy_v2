"""
Author: Armon Dadgar
Description:
  This test tries to initialize a VirtualNamespace and checks that it
  behaves as expected when evaluting in a context
"""

#pragma repy

# Small code snippet, safe
safe_code = "meaning_of_life = 42\n"

# Try to make the safe virtual namespace
safe_virt = createvirtualnamespace(safe_code, "Test VN")

# Create a execution context
context = SafeDict()

# Evaluate
context_2 = safe_virt.evaluate(context)

# Check that the context is the same
if context is not context_2:
  log("Error! Context mis-match!",'\n')

# Check for the meaning of life
if "meaning_of_life" not in context:
  log("Meaning of life is undefined! Existential error!",'\n')


# Try to pass data in, use a plain dict
context = {"info":42}
safe_code = "result = info\n"

# Try to run this
safe_virt = createvirtualnamespace(safe_code, "Test VN 2")

# Evaluate
context_2 = safe_virt.evaluate(context)

# Check the dictionaries are different
if context is context_2:
  log("Error! Plain dictionary output from eval!",'\n')

# Check for the result
if "result" not in context_2:
  log("Result is undefined!",'\n')

if context_2["result"] != 42:
  log("Result is incorrect! Got: ", context_2["result"],'\n')


# We know that the eval() call takes a SafeDict and dict object, but will it take bad inputs?
try:
  safe_virt.evaluate()
  log("Bad! No input allowed for eval!",'\n')
except:
  pass

try:
  safe_virt.evaluate(123)
  log("Bad! Junk input allowed for eval!",'\n')
except:
  pass

