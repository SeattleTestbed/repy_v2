"""
This unit test checks that VirtualNamespace.evaluate() forbids an unsafe context.
"""

# Small code snippet
code = "print 'Bad!'\n"

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
  print "Evaluated with unsafe context!"


