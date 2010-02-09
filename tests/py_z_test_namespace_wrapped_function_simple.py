"""
This tests a wrapped function whose wrapper does as little as possible. The
minimum number of processing functions are passed to the NamespaceAPIFunctionWrapper
constructor and the functions that are passed don't do anything.
"""

import namespace

def foo():
  return "test return value"

foo_func_dict = {
  'func' : foo,
  'args' : [],
  'return' : namespace.Str(),
}

# TODO: Either here or in a separate test we should test the optional
# is_method argument.
foo_wrapper_obj = namespace.NamespaceAPIFunctionWrapper(foo_func_dict)

wrapped_foo = foo_wrapper_obj.wrapped_function

assert(wrapped_foo() == "test return value")
