"""
Verify that VirtualNamespace.evaluate() forbids an unsafe `context`.

Specifically, the `context` that a VirtualNamespace object receives 
must be a `SafeDict`, or parseable as one. This means that the 
context's keys must be of type `str` (which we try to violate in this 
test), avoid particular names / prefixes / components, etc.

Using an unsafe context should raise a `ContextUnsafeError` when 
evaluatinig the VirtualNamespace.

See `safe.py` for what exactly a `SafeDict` is and isn't allowed to 
do and to contain.
"""

#pragma repy 

# Create a virtual namespace with an empty piece of code and a telling name
vn = createvirtualnamespace("", "Bad VN")

# Create a malicious context. (Its key should be `str`, not `int`.)
context = {123: 456}

# Try to evaluate this
try:
  vn.evaluate(context)
except ContextUnsafeError:
  pass
else:
  log("Evaluated with unsafe context!\n")


