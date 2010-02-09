"""
Test the objects wrapped with NamespaceObjectWrapper.
"""

# TODO: Reenable everything related to file objects once those are working
# in repyV2.

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
assert(len(namespace.lock_object_wrapped_functions_dict.keys()) > 0)
assert(len(namespace.tcp_socket_object_wrapped_functions_dict.keys()) > 0)
assert(len(namespace.tcp_server_socket_object_wrapped_functions_dict.keys()) > 0)
assert(len(namespace.udp_server_socket_object_wrapped_functions_dict.keys()) > 0)
assert(len(namespace.virtual_namespace_object_wrapped_functions_dict.keys()) > 0)

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

tcpserversocketobj = emulcomm.tcpserversocket()
tcpsocketobj = emulcomm.emulated_socket(commhandle)
udpserversocketobj = emulcomm.udpserversocket(commhandle)
lockobj = emulmisc.createlock()
open("junk_test.out", "w").close() # touch the file
#fileobj = emulfile.emulated_file("junk_test.out", "r")

wrapped_tcpserversocket = namespace.TCPServerSocket().wrap(tcpserversocketobj)
wrapped_tcpsocket = namespace.TCPSocket().wrap(tcpsocketobj)
wrapped_udpserversocket = namespace.UDPServerSocket().wrap(tcpsocketobj)
wrapped_lock = namespace.Lock().wrap(lockobj)
#wrapped_file = namespace.File().wrap(fileobj)
# TODO: wrapped_virtualnamespace

# Make sure these really are instances of NamespaceObjectWrapper
assert(isinstance(wrapped_tcpserversocket, namespace.NamespaceObjectWrapper))
assert(isinstance(wrapped_tcpsocket, namespace.NamespaceObjectWrapper))
assert(isinstance(wrapped_udpserversocket, namespace.NamespaceObjectWrapper))
assert(isinstance(wrapped_lock, namespace.NamespaceObjectWrapper))
#assert(isinstance(wrapped_file, namespace.NamespaceObjectWrapper))

# Reference attributes that should exist and thus not raise an AttributeError.
wrapped_tcpserversocket.close
wrapped_tcpserversocket.getconnection

wrapped_tcpsocket.close
wrapped_tcpsocket.send
wrapped_tcpsocket.recv

wrapped_udpserversocket.close
wrapped_udpserversocket.getmessage

wrapped_lock.acquire
wrapped_lock.release

#wrapped_file.close
#wrapped_file.readat
#wrapped_file.writeat

# Reference attributes that should *not* exist just to make sure the above
# checks aren't deceptively passing.
try:
  wrapped_tcpsocket.acquire
except AttributeError:
  pass

try:
  wrapped_lock.close
except AttributeError:
  pass

#try:
#  wrapped_file.recv
#except AttributeError:
#  pass

# Make sure that files are iterable but locks are not.
#for line in wrapped_file:
#  pass

try:
  for something in wrapped_lock:
    pass
except TypeError:
  pass

# Try to use a few of the methods of the objects. We didn't start with many
# real objects, so we'll just use the wrappedfile.
#wrapped_file.readat(1024, 0)
#wrapped_file.writeat("test", 0)
#wrapped_file.close()
# Read after close.
#try:
#  wrapped_file.readat(1024, 0)
#except ValueError:
#  pass

# Make sure wrapped commhandle objects expose the hash value of the underlying
# string that is wrapped. For an object to be used as a dictionary key, an
# equality check is also done, so test that as well.
#assert(hash(wrappedcommhandle) == hash(commhandle))
#assert(wrappedcommhandle == commhandle)
#assert(hash(wrappedtimerhandle) == hash(timerhandle))
#assert(wrappedtimerhandle == timerhandle)

# Make sure that other wrapped objects are hashable.
hash(wrapped_tcpserversocket)
hash(wrapped_tcpsocket)
hash(wrapped_udpserversocket)
#hash(wrapped_file)
hash(wrapped_lock)

# Make sure the wrapped objects are comparable (__eq__).
wrapped_tcpserversocket == -1
wrapped_tcpsocket == -1
wrapped_udpserversocket == -1
wrapped_lock == -1
#wrapped_file == -1

# Make sure the wrapped objects are comparable (__ne__).
assert(wrapped_tcpserversocket != -1)
assert(wrapped_tcpsocket != -1)
assert(wrapped_udpserversocket != -1)
assert(wrapped_lock != -1)
#assert(wrapped_file != -1)
