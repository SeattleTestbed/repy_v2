"""
Author: Armon Dadgar
Description:
  This test tries to initialize a VirtualNamespace and checks that it
  behaves as expected when evaluting in a context
"""

if callfunc == "initialize":
  # Small code snippet, safe
  safe_code = "meaning_of_life = 42\n"

  # Try to make the safe virtual namespace
  safe_virt = VirtualNamespace(safe_code)

  # Create a execution context
  context = SafeDict()

  # Evaluate
  context_2 = safe_virt.evaluate(context)

  # Check that the context is the same
  if context is not context_2:
    print "Error! Context mis-match!"

  # Check for the meaning of life
  if "meaning_of_life" not in context:
    print "Meaning of life is undefined! Existential error!"


  # Try to pass data in, use a plain dict
  context = {"info":42}
  safe_code = "result = info\n"

  # Try to run this
  safe_virt = VirtualNamespace(safe_code)

  # Evaluate
  context_2 = safe_virt.evaluate(context)

  # Check the dictionaries are different
  if context is context_2:
    print "Error! Plain dictionary output from eval!"

  # Check for the result
  if "result" not in context_2:
    print "Result is undefined!"

  if context_2["result"] != 42:
    print "Result is incorrect! Got: ", context_2["result"]

  
  # We know that the eval() call takes a SafeDict and dict object, but will it take bad inputs?
  try:
    safe_virt.evaluate()
    print "Bad! No input allowed for eval!"
  except:
    pass

  try:
    safe_virt.evaluate(123)
    print "Bad! Junk input allowed for eval!"
  except:
    pass

