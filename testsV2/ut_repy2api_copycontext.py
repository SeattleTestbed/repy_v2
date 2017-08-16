"""
Check that copy and repr of _context SafeDict don't result in infinite loop
"""
#pragma repy

# Create an "almost" shallow copy of _context, i.e. the contained reference
# to _context is not copied as such but is changed to reference the new
# _context_copy.
# In consequence repr immediately truncates the contained self-reference
# ("{...}") to prevent an infinite loop.
# Caveat: In a real shallow copy, repr would only truncate the context
# contained in the contained context (3rd level).
_context_copy = _context.copy()
repr(_context)
repr(_context_copy)
