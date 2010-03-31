"""
This unit test checks that VirtualNamespace.evaluate() forbids an unsafe context.
"""

#pragma repy 

# Small code snippet
code = "log('Bad!')\n"

# Get a VN
VN = createvirtualnamespace(code, "Bad VN")

# Create a malicious context
context = {"__metaclass__":str}

# Try to evaluate this
try:
  VN.evaluate(context)
except ContextUnsafeError:
  pass
else:
  log("Evaluated with unsafe context!\n")


