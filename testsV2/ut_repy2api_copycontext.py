"""
Check that copy and repr of _context SafeDict don't result in inifinite loop
"""
#pragma repy

# Create an almost shallow copy of _context
# Contained self-reference is moved from _context to _context_copy
_context_copy = _context.copy()
repr(_context)
repr(_context_copy)
