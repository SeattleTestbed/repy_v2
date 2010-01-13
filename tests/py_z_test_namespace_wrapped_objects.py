"""
Test the objects wrapped with NamespaceObjectWrapper.
"""

import namespace  

import emulcomm
import emulfile
import emulmisc
import socket

import repyportability

# We call namespace.wrap_and_insert_api_functions() because this will ensure
# that any required namespace module initialization is also done. Normally
# code would never need to worry about side effects of that function such
# as initializing the module because that is the only function of the module
# that is used (except in tests like this one).
usercontext = {}
namespace.wrap_and_insert_api_functions(usercontext)

# Make sure that the wrappers for the methods of objects we may use have been
# setup.
assert(len(namespace.file_object_wrapped_functions_dict.keys()) > 0)
assert(len(namespace.socket_object_wrapped_functions_dict.keys()) > 0)
assert(len(namespace.lock_object_wrapped_functions_dict.keys()) > 0)

# Check one of these dictionaries' values. They should all be wrapped functions.
for func_name in namespace.file_object_wrapped_functions_dict:
  # Use some special python stuff. A method's im_class attribute will be the
  # class that the method's owning instance is an instance of. We just want
  # to make sure every value in the dictionary is a
  # NamespaceAPIFunctionWrapper.wrapped_function()
  assert(namespace.file_object_wrapped_functions_dict[func_name].im_class is namespace.NamespaceAPIFunctionWrapper)
  assert(namespace.file_object_wrapped_functions_dict[func_name].__name__ == "wrapped_function")

# Create one of each type of object that gets wrapped.
commhandle = "fakecommhandle"

# Armon: Create handle entry...
emulcomm.comminfo[commhandle] = {"socket":socket.socket()}

timerhandle = "faketimerhandle"
socketobj = emulcomm.emulated_socket(commhandle)
lockobj = emulmisc.getlock()
open("junk_test.out", "w").close() # touch the file
fileobj = emulfile.emulated_file("junk_test.out", "r")

wrappedcommhandle = namespace.wrap_commhandle_obj(commhandle)
wrappedtimerhandle = namespace.wrap_timerhandle_obj(timerhandle)
wrappedsocket = namespace.wrap_socket_obj(socketobj)
wrappedlock = namespace.wrap_lock_obj(lockobj)
wrappedfile = namespace.wrap_file_obj(fileobj)

# Make sure these really are instances of NamespaceObjectWrapper
assert(isinstance(wrappedcommhandle, namespace.NamespaceObjectWrapper))
assert(isinstance(wrappedtimerhandle, namespace.NamespaceObjectWrapper))
assert(isinstance(wrappedsocket, namespace.NamespaceObjectWrapper))
assert(isinstance(wrappedlock, namespace.NamespaceObjectWrapper))
assert(isinstance(wrappedfile, namespace.NamespaceObjectWrapper))

# Reference attributes that should exist and thus not raise an AttributeError.
wrappedsocket.close
wrappedsocket.send
wrappedsocket.recv
wrappedsocket.willblock

wrappedlock.acquire
wrappedlock.release

wrappedfile.close
wrappedfile.flush
wrappedfile.next
wrappedfile.read
wrappedfile.readline
wrappedfile.readlines
wrappedfile.seek
wrappedfile.write
wrappedfile.writelines

# Reference attributes that should *not* exist just to make sure the above
# checks aren't deceptively passing.
try:
  wrappedsocket.acquire
except AttributeError:
  pass

try:
  wrappedlock.close
except AttributeError:
  pass

try:
  wrappedfile.recv
except AttributeError:
  pass

# Make sure that files are iterable but locks are not.
for line in wrappedfile:
  pass

try:
  for something in wrappedlock:
    pass
except TypeError:
  pass

# Try to use a few of the methods of the objects. We didn't start with many
# real objects, so we'll just use the wrappedfile.
wrappedfile.read()
wrappedfile.seek(0)
wrappedfile.readlines()
wrappedfile.close()
# Read after close.
try:
  wrappedfile.read(1)
except ValueError:
  pass

# Make sure wrapped commhandle objects expose the hash value of the underlying
# string that is wrapped. For an object to be used as a dictionary key, an
# equality check is also done, so test that as well.
assert(hash(wrappedcommhandle) == hash(commhandle))
assert(wrappedcommhandle == commhandle)
assert(hash(wrappedtimerhandle) == hash(timerhandle))
assert(wrappedtimerhandle == timerhandle)

# Make sure that other wrapped objects are hashable.
hash(wrappedfile)
hash(wrappedlock)
hash(wrappedsocket)

# Make sure the wrapped objects are comparable (__eq__).
wrappedcommhandle == -1
wrappedtimerhandle == -1 
wrappedsocket == -1
wrappedlock == -1
wrappedfile == -1

# Make sure the wrapped objects are comparable (__ne__).
assert(wrappedcommhandle != -1)
assert(wrappedtimerhandle != -1)
assert(wrappedsocket != -1)
assert(wrappedlock != -1)
assert(wrappedfile != -1)

