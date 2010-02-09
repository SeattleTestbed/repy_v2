
import namespace

usercontext = {}
namespace.wrap_and_insert_api_functions(usercontext)

assert(len(usercontext.keys()) > 0)
assert(len(usercontext.keys()) == len(namespace.USERCONTEXT_WRAPPER_INFO.keys()))

# Make sure a few expected items are there.
usercontext["openfile"]
usercontext["listfiles"]
usercontext["removefile"]
usercontext["exitall"]

for func_name in namespace.USERCONTEXT_WRAPPER_INFO:
  # Use some special python stuff. A method's im_class attribute will be the
  # class that the method's owning instance is an instance of. We just want
  # to make sure every value in the dictionary is a
  # NamespaceAPIFunctionWrapper.wrapped_function()
  assert(usercontext[func_name].im_class is namespace.NamespaceAPIFunctionWrapper)
  assert(usercontext[func_name].__name__ == "wrapped_function")
