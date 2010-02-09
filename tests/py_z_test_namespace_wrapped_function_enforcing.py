"""
This tests all of the processing functions that can be provided for a wrapped
function.
"""

import namespace

from exception_hierarchy import *


# Patch the namespace so that situations that would cause an exit don't really
# cause the program to exit.

class WouldHaveExited(Exception):
  pass


def _exit_exception_raiser(message, exitcode):
  raise WouldHaveExited(message)


namespace._handle_internalerror = _exit_exception_raiser


class FakeAllowedError(RepyException):
  pass


class FakeForbiddenError(Exception):
  pass


def foo(testarg):
  if testarg == 1:
    return "test return value"
  elif testarg == 2:
    return 1
  elif testarg == 3:
    raise FakeAllowedError
  else:
    raise FakeForbiddenError


foo_func_dict = {
  'func' : foo,
  'args' : [namespace.Int()],
  'return' : namespace.Str(),
}

foo_wrapper_obj = namespace.NamespaceAPIFunctionWrapper(foo_func_dict)

wrapped_foo = foo_wrapper_obj.wrapped_function

# The returned string should be wrapped in a list.
assert(wrapped_foo(1) == "test return value")

# Try disallowed arguments (only a single int is allowed by the arg_checking_func).
# We expect it to raise a TypeError.
try:
  wrapped_foo("abc")
except RepyArgumentError:
  pass
else:
  raise Exception("Expected exception wasn't raised.")

# Try disallowed arguments (no args at all is not allowed by the arg_checking_func).
try:
  wrapped_foo()
except RepyArgumentError:
  pass
else:
  raise Exception("Expected exception wasn't raised.")

# Try disallowed return value (int instead of string).
try:
  wrapped_foo(2)
except WouldHaveExited:
  pass
else:
  raise Exception("Expected exception wasn't raised.")

# Try allowed exceptions.
try:
  wrapped_foo(3)
except FakeAllowedError:
  pass
else:
  raise Exception("Expected exception wasn't raised.")

# Try disallowed exceptions.
try:
  wrapped_foo(4)
except WouldHaveExited:
  pass
else:
  raise Exception("Expected exception wasn't raised.")
