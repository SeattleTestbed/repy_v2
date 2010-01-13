"""
This tests all of the processing functions that can be provided for a wrapped
function.
"""

import namespace



class FakeAllowedException(Exception):
  pass

class FakeForbiddenException(Exception):
  pass



def foo(testarg):
  if testarg == 1:
    return "test return value"
  elif testarg == 2:
    return 123
  elif testarg == 3:
    raise FakeAllowedException
  else:
    raise FakeForbiddenException



def arg_checking_func(*args, **kwargs):
  if len(args) != 1 or len(kwargs.keys()) > 0:
    raise namespace.NamespaceRequirementError
  if type(args[0]) is not int:
    raise namespace.NamespaceRequirementError



def return_checking_func(retval):
  if type(retval) is not str:
    raise namespace.NamespaceRequirementError



def exception_checking_func(exc):
  if not isinstance(exc, FakeAllowedException):
    raise namespace.NamespaceRequirementError



arg_wrapping_func_call_count = 0

def arg_wrapping_func(*args, **kwargs):
  # We wrap the first arg in a dict.
  global arg_wrapping_func_call_count
  arg_wrapping_func_call_count += 1

  wrapped = {"firstarg" : args[0]}
  return [wrapped], kwargs



arg_unwrapping_func_call_count = 0

def arg_unwrapping_func(*args, **kwargs):
  # We take the item out of the dict we just wrapped it in.

  global arg_unwrapping_func_call_count
  arg_unwrapping_func_call_count += 1

  unwrapped = args[0]["firstarg"]
  return [unwrapped], kwargs



def return_wrapping_func(retval):
  return [retval]



foo_func_dict = {
  'target_func' : foo,
  'arg_checking_func' : arg_checking_func,
  'return_checking_func' : return_checking_func,
  'exception_checking_func' : exception_checking_func,
  'arg_wrapping_func' : arg_wrapping_func,
  'arg_unwrapping_func' : arg_unwrapping_func,
  'return_wrapping_func' : return_wrapping_func,
}

foo_wrapper_obj = namespace.NamespaceAPIFunctionWrapper(foo_func_dict)

wrapped_foo = foo_wrapper_obj.wrapped_function

# The returned string should be wrapped in a list.
assert(wrapped_foo(1)[0] == "test return value")

# Make sure the arg wrapping/unwrapping functions really did get called, as the
# way we have them setup everything would work correctly even if they weren't
# called.
assert(arg_wrapping_func_call_count == 1)
assert(arg_unwrapping_func_call_count == 1)

# Try disallowed arguments (only a single int is allowed by the arg_checking_func).
# We expect it to raise a TypeError.
try:
  wrapped_foo("abc")
except TypeError:
  pass

# Try disallowed arguments (no args at all is not allowed by the arg_checking_func).
# We expect it to raise a TypeError.
try:
  wrapped_foo()
except TypeError:
  pass

# Try disallowed return value (the function foo will return an int when
# the argument is the the integer 2).
try:
  wrapped_foo(2)
except namespace.NamespaceViolationError:
  pass

# Try allowed exceptions.
# We expect the FakeAllowedException raised in foo() to be raised here.
try:
  wrapped_foo(3)
except FakeAllowedException:
  pass

# Try disallowed exceptions.
try:
  wrapped_foo(4)
except namespace.NamespaceViolationError:
  pass

