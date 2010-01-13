"""
This tests a wrapped function whose wrapper does as little as possible. The
minimum number of processing functions are passed to the NamespaceAPIFunctionWrapper
constructor and the functions that are passed don't do anything.
"""

import namespace

def foo():
  return "test return value"

def noop(*args, **kwargs):
  pass

foo_func_dict = {
  'target_func' : foo,
  'arg_checking_func' : noop,
  'return_checking_func' : noop,
  'exception_checking_func' : noop,
  # Optional and we aren't using them in this test.
  #'arg_wrapping_func' : None,
  #'arg_unwrapping_func' : None,
  #'return_wrapping_func' : None,
}

foo_wrapper_obj = namespace.NamespaceAPIFunctionWrapper(foo_func_dict)

wrapped_foo = foo_wrapper_obj.wrapped_function

assert(wrapped_foo() == "test return value")

