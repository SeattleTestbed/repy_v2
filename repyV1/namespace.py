"""
<Program>
  namespace.py

<Started>
  September 2009

<Author>
  Justin Samuel

<Purpose>
  This is the namespace layer that ensures separation of the namespaces of
  untrusted code and our code. It provides a single public function to be
  used to setup the context in which untrusted code is exec'd (that is, the
  context that is seen as the __builtins__ by the untrusted code).
  
  The general idea is that any function or object that is available between
  trusted and untrusted code gets wrapped in a function or object that does
  validation when the function or object is used. In general, if user code
  is not calling any functions improperly, neither the user code nor our
  trusted code should ever notice that the objects and functions they are
  dealing with have been wrapped by this namespace layer.
  
  All of our own api functions are wrapped in NamespaceAPIFunctionWrapper
  objects whose wrapped_function() method is mapped in to the untrusted
  code's context. When called, the wrapped_function() method performs
  argument, return value, and exception validation as well as additional
  wrapping and unwrapping, as needed, that is specific to the function
  that was ultimately being called. If the return value or raised exceptions
  are not considered acceptable, a NamespaceViolationError is raised. If the
  arguments are not acceptable, a TypeError is raised.
  
  Note that callback functions that are passed from untrusted user code
  to trusted code are also wrapped (these are arguments to wrapped API
  functions, so we get to wrap them before calling the underlying function).
  The reason we wrap these is so that we can intercept calls to the callback
  functions and wrap arguments passed to them, making sure that handles
  passed as arguments to the callbacks get wrapped before user code sees them.
  
  The function and object wrappers have been defined based on the API as
  documented at https://seattle.cs.washington.edu/wiki/RepyLibrary
  
  Example of using this module (this is really the only way to use the module):
  
    import namespace  
    usercontext = {}
    namespace.wrap_and_insert_api_functions(usercontext)
    safe.safe_exec(usercode, usercontext)
  
  The above code will result in the dict usercontext being populated with keys
  that are the names of the functions available to the untrusted code (such as
  'open') and the values are the wrapped versions of the actual functions to be
  called (such as 'emulfile.emulated_open').
  
  Note that some functions wrapped by this module lose some python argument
  flexibility. Wrapped functions can generally only have keyword args in
  situations where the arguments are optional. Using keyword arguments for
  required args may not be supported, depending on the implementation of the
  specific argument check/wrapping/unwrapping helper functions for that
  particular wrapped function. If this becomes a problem, it can be dealt with
  by complicating some of the argument checking/wrapping/unwrapping code in
  this module to make the checking functions more flexible in how they take
  their arguments.
  
  Implementation details:
  
  The majority of the code in this module is made up of helper functions to do
  argument checking, etc. for specific wrapped functions.
  
  The most important parts to look at in this module for maintenance and
  auditing are the following:
  
    USERCONTEXT_WRAPPER_INFO
    
      The USERCONTEXT_WRAPPER_INFO is a dictionary that defines the API
      functions that are wrapped and inserted into the user context when
      wrap_and_insert_api_functions() is called.
    
    FILE_OBJECT_WRAPPER_INFO
    SOCKET_OBJECT_WRAPPER_INFO
    LOCK_OBJECT_WRAPPER_INFO
    VIRTUAL_NAMESPACE_OBJECT_WRAPPER_INFO
    
      The above four dictionaries define the methods available on the wrapped
      objects that are returned by wrapped functions. Additionally, timerhandle
      and commhandle objects are wrapped but instances of these do not have any
      public methods and so no *_WRAPPER_INFO dictionaries are defined for them.
  
    NamespaceObjectWrapper
    NamespaceAPIFunctionWrapper
  
      The above two classes are the only two types of objects that will be
      allowed in untrusted code. In fact, instances of NamespaceAPIFunctionWrapper
      are never actually allowed in untrusted code. Rather, each function that
      is wrapped has a single NamespaceAPIFunctionWrapper instance created
      when wrap_and_insert_api_functions() is called and what is actually made
      available to the untrusted code is the wrapped_function() method of each
      of the corresponding NamespaceAPIFunctionWrapper instances.
      
    NamespaceViolationError
    
      This is the error that is raised from a wrapped function if any namespace
      violation occurs other than invalid arguments. Invalid arguments raise
      a TypeError to keep the behavior compatible with python's normal way of
      handling numbers of or names of arguments.
"""

import types

# To check if objects are thread.LockType objects.
import thread

import emulfile
import emultimer
import emulcomm
import emulmisc

# Used to get SafeDict
import safe

# Used to get VirtualNamespace
import virtual_namespace

# Save a copy of a few functions not available at runtime.
_saved_getattr = getattr
_saved_callable = callable
_saved_id = id


##############################################################################
# Public functions of this module to be called from the outside.
##############################################################################

def wrap_and_insert_api_functions(usercontext):
  """
  This is the main public function in this module at the current time. It will
  wrap each function in the usercontext dict in a wrapper with custom
  restrictions for that specific function. These custom restrictions are
  defined in the dictionary USERCONTEXT_WRAPPER_INFO.
  """
  
  _init_namespace()
  
  for function_name in USERCONTEXT_WRAPPER_INFO:
    function_info = USERCONTEXT_WRAPPER_INFO[function_name]
    wrapperobj = NamespaceAPIFunctionWrapper(function_info)
    usercontext[function_name] = wrapperobj.wrapped_function





##############################################################################
# Helper functions for the above public function.
##############################################################################

# Whether _init_namespace() has already been called.
initialized = False

def _init_namespace():
  """
  Performs one-time initialization of the namespace module.
  """
  global initialized
  if not initialized:
    initialized = True
    _prepare_wrapped_functions_for_object_wrappers()





# These dictionaries will ultimately contain keys whose names are allowed
# methods that can be called on the objects and values which are the wrapped
# versions of the functions which are exposed to users. If a dictionary
# is empty, it means no methods can be called on a wrapped object of that type.
file_object_wrapped_functions_dict = {}
socket_object_wrapped_functions_dict = {}
lock_object_wrapped_functions_dict = {}
virtual_namespace_object_wrapped_functions_dict = {}

def _prepare_wrapped_functions_for_object_wrappers():
  """
  Wraps functions that will be used whenever a wrapped object is created.
  After this has been called, the dictionaries such as
  file_object_wrapped_functions_dict have been populated and therefore can be
  used by functions such as wrap_socket_obj().
  """
  objects_tuples = [(FILE_OBJECT_WRAPPER_INFO, file_object_wrapped_functions_dict),
                    (SOCKET_OBJECT_WRAPPER_INFO, socket_object_wrapped_functions_dict),
                    (LOCK_OBJECT_WRAPPER_INFO, lock_object_wrapped_functions_dict),
                    (VIRTUAL_NAMESPACE_OBJECT_WRAPPER_INFO, virtual_namespace_object_wrapped_functions_dict)]
  
  for description_dict, wrapped_func_dict in objects_tuples:
    for function_name in description_dict:
      function_info = description_dict[function_name]
      wrapperobj = NamespaceAPIFunctionWrapper(function_info)
      wrapped_func_dict[function_name] = wrapperobj.wrapped_function





##############################################################################
# Helper functions that raise NamespaceRequirementError if the argument
# does not meet the required conditions.
##############################################################################

class NamespaceRequirementError(Exception):
  """
  Indicates that some namespace requirement has not been met. This is not an
  exception that should be returned to the user. Instead, it is to signal to
  our own code that there is a violation. We then raise a
  NamespaceViolationError which will be seen by the offending user code.
  """



def _is_in(obj, sequence):
  """
  A helper function to do identity ("is") checks instead of equality ("==")
  when using X in [A, B, C] type constructs. So you would write:
    if _is_in(type(foo), [int, long]):
  instead of:
    if type(foo) in [int, long]:
  """
  for item in sequence:
    if obj is item:
      return True
  return False
  



def _require_string(obj):
  if not _is_in(type(obj), [str, unicode]):
    raise NamespaceRequirementError



def _require_integer(obj):
  if not _is_in(type(obj), [int, long]):
    raise NamespaceRequirementError



def _require_float(obj):
  if type(obj) is not float:
    raise NamespaceRequirementError



def _require_integer_or_float(obj):
  if not _is_in(type(obj), [int, long, float]):
    raise NamespaceRequirementError



def _require_bool(obj):
  if type(obj) is not bool:
    raise NamespaceRequirementError



def _require_bool_or_integer(obj):
  if not _is_in(type(obj), [bool, int, long]):
    raise NamespaceRequirementError



def _require_tuple(obj):
  if type(obj) is not tuple:
    raise NamespaceRequirementError



def _require_list(obj):
  if type(obj) is not list:
    raise NamespaceRequirementError



def _require_tuple_or_list(obj):
  if not _is_in(type(obj), [tuple, list]):
    raise NamespaceRequirementError



def _require_user_function(obj):
  if not _is_in(type(obj), [types.FunctionType, types.LambdaType, types.MethodType]):
    raise NamespaceRequirementError



def _require_list_of_strings(obj):
  _require_list(obj)
  for item in obj:
    _require_string(item)


def _require_dict_or_safedict(obj):
  if type(obj) is not dict and not isinstance(obj, safe.SafeDict):
    raise NamespaceRequirementError

def _require_safedict(obj):
  if not isinstance(obj, safe.SafeDict):
    raise NamespaceRequirementError


##############################################################################
# Functions that are used in the USERCONTEXT_WRAPPER_INFO to defined how each
# wrapper should be constructed. These raise NamespaceRequirementError if
# something is not considered acceptable.
##############################################################################

def allow_all(*args, **kwargs):
  pass



def allow_no_args(*args, **kwargs):
  if len(args) != 0 or len(kwargs.keys()) != 0:
    raise NamespaceRequirementError("No arguments allowed.")



def allow_args_single_integer_or_float(*args, **kwargs):
  if len(args) != 1:
    raise NamespaceRequirementError
  if len(kwargs.keys()) != 0:
    raise NamespaceRequirementError
  _require_integer_or_float(args[0])



def allow_return_none(retval):
  if retval is not None:
    raise NamespaceRequirementError



def allow_return_integer(retval):
  _require_integer(retval)



def allow_return_float(retval):
  _require_float(retval)



def allow_return_bool(retval):
  _require_bool(retval)


# Armon: Boolean tuple with exactly 2 elements
def allow_return_two_bools_tuple(retval):
  # First validate it is a boolean tuple
  _require_tuple(retval)
  for elem in retval:
    _require_bool(elem)

  # Check the size of the tuple is exactly 2
  if len(retval) != 2:
    raise NamespaceRequirementError



def allow_args_single_string(*args, **kwargs):
  if len(args) != 1:
    raise NamespaceRequirementError
  if len(kwargs.keys()) != 0:
    raise NamespaceRequirementError
  _require_string(args[0])



def allow_return_string(retval):
  _require_string(retval)



def allow_return_gethostbyname_ex(retval):
  _require_tuple(retval)
  if len(retval) != 3:
    raise NamespaceRequirementError

  hostname, aliaslist, ipaddrlist = retval

  _require_string(hostname)
  _require_list_of_strings(aliaslist)
  _require_list_of_strings(ipaddrlist)



def allow_args_recvmess_callback(remoteIP, remoteport, message, commhandle):
  # The callback function should receive the following arguments:
  # (remoteIP, remoteport, message, commhandle)
  
  _require_string(remoteIP)
  _require_integer(remoteport)
  _require_string(message)
  
  # There isn't much to check with the commhandle as once it is wrapped
  # there isn't any way user code can interact with it.



def wrap_args_recvmess_callback(remoteIP, remoteport, message, commhandle):
  """
  Wrap the commhandle passed into the callback function before the callback
  function is actually called.
  """
  # The callback function should receive the following arguments:
  # (remoteIP, remoteport, message, commhandle)

  wrapped_commhandle = wrap_commhandle_obj(commhandle)
  
  args = (remoteIP, remoteport, message, wrapped_commhandle)
  kwargs = {}
  return args, kwargs



def allow_args_recvmess(localip, localport, function):
  _require_string(localip)
  _require_integer(localport)
  _require_user_function(function)



def wrap_args_recvmess(localip, localport, function):
  """
  Wrap the callback function passed from user code to privileged code. This is
  done so that we can intercept calls to the callback function and check and
  wrap arguments passed into the untrusted callback function.
  """

  function_info = {'target_func' : function,
                   'arg_checking_func' : allow_args_recvmess_callback,
                   'arg_wrapping_func' : wrap_args_recvmess_callback,
                   'return_checking_func' : allow_all}
  
  wrapperobj = NamespaceAPIFunctionWrapper(function_info)
  
  args = (localip, localport, wrapperobj.wrapped_function)
  kwargs = {}
  return args, kwargs



def allow_args_sendmess(desthost, destport, message, localip=None, localport=None):

  _require_string(desthost)
  _require_integer(destport)
  _require_string(message)

  # The user must provide either both or neither of localip and localport,
  # but we're going to let the actual sendmess worry about that.
  if localip is not None:
    _require_string(localip)
  if localport is not None:
    _require_integer(localport)



def allow_args_openconn(desthost, destport, localip=None, localport=0, timeout=5):
  # TODO: the wiki:RepyLibrary gives localport=0 as the default for this function,
  # slightly different than the localport=None it gives for sendmess(). This
  # should either be verified as intentional or made the same.

  _require_string(desthost)
  _require_integer(destport)

  # The user must provide either both or neither of localip and localport,
  # but we're going to let the actual sendmess worry about that.
  if localip is not None:
    _require_string(localip)
  # We accept a localport of None to mean the same thing as 0.
  if localport is not None:
    _require_integer(localport)

  # We accept a timeout of None to mean the same as 0.
  if timeout is not None:
    _require_integer_or_float(timeout)



def allow_args_waitforconn_callback(remoteip, remoteport, socketlikeobj, thiscommhandle, listencommhandle):
  # The callback function should receive the following arguments:
  # (remoteip, remoteport, socketlikeobj, thiscommhandle, listencommhandle)
  
  _require_string(remoteip)
  _require_integer(remoteport)
  _require_emulated_socket(socketlikeobj)
  # There isn't much to check with the commhandles as once they are wrapped
  # there isn't any way user code can interact with them.
  


def wrap_args_waitforconn_callback(remoteip, remoteport, socketlikeobj, thiscommhandle, listencommhandle):
  """
  Wrap the socketlikeobj, thiscommhandle, listencommhandle passed into the
  callback function before the callback function is actually called.
  """
  # The callback function should receive the following arguments:
  # (remoteip, remoteport, socketlikeobj, thiscommhandle, listencommhandle)

  wrapped_socketlikeobj = wrap_socket_obj(socketlikeobj)
  wrapped_thiscommhandle = wrap_commhandle_obj(thiscommhandle)
  wrapped_listencommhandle = wrap_commhandle_obj(listencommhandle)
  
  args = (remoteip, remoteport, wrapped_socketlikeobj, wrapped_thiscommhandle,
          wrapped_listencommhandle)
  kwargs = {}
  return args, kwargs



def allow_args_waitforconn(localip, localport, function):
  _require_string(localip)
  _require_integer(localport)
  _require_user_function(function)



def wrap_args_waitforconn(localip, localport, function):
  """
  Wrap the callback function passed from user code to privileged code. This is
  done so that we can intercept calls to the callback function and check and
  wrap arguments passed into the untrusted callback function.
  """

  function_info = {'target_func' : function,
                   'arg_checking_func' : allow_args_waitforconn_callback,
                   'arg_wrapping_func' : wrap_args_waitforconn_callback,
                   'return_checking_func' : allow_all}
  
  wrapperobj = NamespaceAPIFunctionWrapper(function_info)
  
  args = (localip, localport, wrapperobj.wrapped_function)
  kwargs = {}
  return args, kwargs







def allow_args_stopcomm(wrapped_commhandle):
  try:
    if wrapped_commhandle._wrapped__type_name != "commhandle":
      raise NamespaceRequirementError
  except AttributeError:
    raise NamespaceRequirementError




def allow_args_open(filename, mode='r'):
  _require_string(filename)
  _require_string(mode)



def allow_return_list_of_strings(retval):
  _require_list_of_strings(retval)



def allow_args_settimer(waittime, function, args):
  _require_integer_or_float(waittime)
  _require_user_function(function)
  _require_tuple_or_list(args)



def allow_args_canceltimer(wrapped_timerhandle):
  try:
    if wrapped_timerhandle._wrapped__type_name != "timerhandle":
      raise NamespaceRequirementError
  except AttributeError:
    raise NamespaceRequirementError


def allow_args_virtual_namespace(code, name="<string>"):
  _require_string(code)
  _require_string(name)


def wrap_commhandle_obj(commhandle):
  # There are no attributes to be accessed on commhandles.
  return NamespaceObjectWrapper("commhandle", commhandle, [])



def wrap_timerhandle_obj(timerhandle):
  # There are no attributes to be accessed on timerhandles.
  return NamespaceObjectWrapper("timerhandle", timerhandle, [])



def wrap_socket_obj(socketobj):
  _require_emulated_socket(socketobj)
  return NamespaceObjectWrapper("socket", socketobj, socket_object_wrapped_functions_dict)



def wrap_lock_obj(lockobj):
  _require_lock_object(lockobj)
  return NamespaceObjectWrapper("lock", lockobj, lock_object_wrapped_functions_dict)



def wrap_file_obj(fileobj):
  _require_emulated_file(fileobj)
  return NamespaceObjectWrapper("file", fileobj, file_object_wrapped_functions_dict)

def wrap_virtual_namespace_obj(virt):
  _require_virtual_namespace_object(virt)
  return NamespaceObjectWrapper("VirtualNamespace", virt, virtual_namespace_object_wrapped_functions_dict)


def unwrap_single_arg(*args, **kwargs):
  unwrapped_args = (args[0]._wrapped__object,)
  unwrapped_kwargs = {}
  return unwrapped_args, unwrapped_kwargs



##############################################################################
# Constants that define which functions should be wrapped and how. These are
# used by the functions wrap_and_insert_api_functions() and
# wrap_builtin_functions().
##############################################################################

# These are the functions in the user's name space excluding the builtins we
# allow. Each function is a key in the dictionary. Each value is a dictionary
# that defines the functions to be used by the wrapper when a call is
# performed. It is the same dictionary that is passed as a constructor to
# the NamespaceAPIFunctionWrapper class to create the actual wrappers.
# The public function wrap_and_insert_api_functions() uses this dictionary as
# the basis for what is populated in the user context. Anything function
# defined here will be wrapped and made available to untrusted user code.
USERCONTEXT_WRAPPER_INFO = {
  # emulated open function
  'open' :
      {'target_func' : emulfile.emulated_open,
       'arg_checking_func' : allow_args_open,
       # Even though the checking function is allow_all, the wrapping function
       # does check the type.
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_file_obj},

  # emulated file object
  'file' :
      {'target_func' : emulfile.emulated_open,
       'arg_checking_func' : allow_args_open,
       # Even though the checking function is allow_all, the wrapping function
       # does check the type.
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_file_obj},

  # List the files in the sandboxed program's area
  'listdir' :
      {'target_func' : emulfile.listdir,
       'arg_checking_func' : allow_no_args,
       'return_checking_func' : allow_return_list_of_strings},

  # remove a file in the sandboxed program's area
  'removefile' :
      {'target_func' : emulfile.removefile,
       'arg_checking_func' : allow_args_single_string,
       'return_checking_func' : allow_return_none},

  # provides an external IP
  'getmyip' :
      {'target_func' : emulcomm.getmyip,
       'arg_checking_func' : allow_no_args,
       'return_checking_func' : allow_return_string},

  # same as socket method
  'gethostbyname_ex' :
      {'target_func' : emulcomm.gethostbyname_ex,
       'arg_checking_func' : allow_args_single_string,
       'return_checking_func' : allow_return_gethostbyname_ex},

  # message receive (UDP)
  'recvmess' :
      {'target_func' : emulcomm.recvmess,
       'arg_checking_func' : allow_args_recvmess,
       'arg_wrapping_func' : wrap_args_recvmess,
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_commhandle_obj},

  # message sending (UDP)
  'sendmess' :
      {'target_func' : emulcomm.sendmess,
       'arg_checking_func' : allow_args_sendmess,
       'return_checking_func' : allow_return_integer},

  # reliable comm channel (TCP)
  'openconn' :
      {'target_func' : emulcomm.openconn,
       'arg_checking_func' : allow_args_openconn,
       # Even though the checking function is allow_all, the wrapping function
       # does check the type.
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_socket_obj},

  # reliable comm listen (TCP)
  'waitforconn' :
      {'target_func' : emulcomm.waitforconn,
       'arg_checking_func' : allow_args_waitforconn,
       'arg_wrapping_func' : wrap_args_waitforconn,
       # There isn't much to check in terms of the return value as the commhandle
       # wrapper doesn't let anything be done to the wrapped object.
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_commhandle_obj},

  # stop receiving (TCP/UDP)
  'stopcomm' :
      {'target_func' : emulcomm.stopcomm,
       'arg_checking_func' : allow_args_stopcomm,
       'arg_unwrapping_func' : unwrap_single_arg,
       'return_checking_func' : allow_return_bool},

  # sets a timer
  'settimer' :
      {'target_func' : emultimer.settimer,
       'arg_checking_func' : allow_args_settimer,
       # There isn't much to check in terms of the return value as the timerhandle
       # wrapper doesn't let anything be done to the wrapped object.
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_timerhandle_obj},

  # stops a timer if it hasn't fired
  'canceltimer' :
      {'target_func' : emultimer.canceltimer,
       'arg_checking_func' : allow_args_canceltimer,
       'arg_unwrapping_func' : unwrap_single_arg,
       'return_checking_func' : allow_return_bool},

  # blocks the thread for some time
  'sleep' :
      {'target_func' : emultimer.sleep,
       'arg_checking_func' : allow_args_single_integer_or_float,
       'return_checking_func' : allow_return_none},

  # same as random.random()
  'randomfloat' :
      {'target_func' : emulmisc.randomfloat,
       'arg_checking_func' : allow_no_args,
       'return_checking_func' : allow_return_float},

  # amount of time the program has run
  'getruntime' :
      {'target_func' : emulmisc.getruntime,
       'arg_checking_func' : allow_no_args,
       'return_checking_func' : allow_return_float},

  # acquire a lock object
  'getlock' :
      {'target_func' : emulmisc.getlock,
       'arg_checking_func' : allow_no_args,
       # Even though the checking function is allow_all, the wrapping function
       # does check the type.
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_lock_obj},

  # Stops executing the sandboxed program
  'exitall' :
      {'target_func' : emulmisc.exitall,
       'arg_checking_func' : allow_no_args,
       'return_checking_func' : allow_return_none},

  # Provides an unique identifier for the current thread
  'get_thread_name' :
      {'target_func' : emulmisc.get_thread_name,
       'arg_checking_func' : allow_no_args,
       'return_checking_func' : allow_return_string},

  # Provides a safe execution environment for arbitrary code
  'VirtualNamespace' :
      {'target_func' : virtual_namespace.get_VirtualNamespace,
       'arg_checking_func' : allow_args_virtual_namespace,
       'return_checking_func' : allow_all,
       'return_wrapping_func' : wrap_virtual_namespace_obj}
}





def _require_emulated_file(fileobj):
  if not isinstance(fileobj, emulfile.emulated_file):
    raise NamespaceRequirementError("Expected emulated_file, received " + str(fileobj))



def allow_args_emulated_file(file):
  _require_emulated_file(file)



def allow_args_emulated_file_and_optional_integer(*args, **kwargs):
  # First arg is self, which is required.
  if len(args) not in [1, 2]:
    raise NamespaceRequirementError
  
  if len(kwargs.keys()) != 0:
    raise NamespaceRequirementError
  
  _require_emulated_file(args[0])
  
  # If the user did provide the optional single integer, make sure it's an int.
  if len(args) == 2:
    _require_integer(args[1])



def allow_args_emulated_file_seek(fileobj, offset, whence=0):
  _require_emulated_file(fileobj)
  # Note: offset can be negative. Resist the urge to require it to be
  # non-negative.
  _require_integer(offset)
  _require_integer(whence)



def allow_args_emulated_file_write(fileobj, data):
  _require_emulated_file(fileobj)
  _require_string(data)



def allow_args_emulated_file_writelines(fileobj, lines):
  _require_emulated_file(fileobj)
  _require_list_of_strings(lines)
  
  

FILE_OBJECT_WRAPPER_INFO = {
  'close' :
      {'target_func' : emulfile.emulated_file.close,
       'arg_checking_func' : allow_args_emulated_file,
       'return_checking_func' : allow_return_none},
       
  'flush' :
      {'target_func' : emulfile.emulated_file.flush,
       'arg_checking_func' : allow_args_emulated_file,
       'return_checking_func' : allow_return_none},

  'next' :
      {'target_func' : emulfile.emulated_file.next,
       'arg_checking_func' : allow_args_emulated_file,
       'return_checking_func' : allow_return_string},

  'read' :
      {'target_func' : emulfile.emulated_file.read,
       'arg_checking_func' : allow_args_emulated_file_and_optional_integer,
       'return_checking_func' : allow_return_string},

  'readline' :
      {'target_func' : emulfile.emulated_file.readline,
       'arg_checking_func' : allow_args_emulated_file_and_optional_integer,
       'return_checking_func' : allow_return_string},

  'readlines' :
      {'target_func' : emulfile.emulated_file.readlines,
       'arg_checking_func' : allow_args_emulated_file_and_optional_integer,
       'return_checking_func' : allow_return_list_of_strings},
       
  'seek' :
      {'target_func' : emulfile.emulated_file.seek,
       'arg_checking_func' : allow_args_emulated_file_seek,
       'return_checking_func' : allow_return_none},
       
  'write' :
      {'target_func' : emulfile.emulated_file.write,
       'arg_checking_func' : allow_args_emulated_file_write,
       'return_checking_func' : allow_return_none},
       
  'writelines' :
      {'target_func' : emulfile.emulated_file.writelines,
       'arg_checking_func' : allow_args_emulated_file_writelines,
       'return_checking_func' : allow_return_none},
}






def _require_emulated_socket(socket):
  if not isinstance(socket, emulcomm.emulated_socket):
    raise NamespaceRequirementError("Expected emulated_socket, received " + str(socket))



def allow_args_emulated_socket(socket):
  _require_emulated_socket(socket)



def allow_args_emulated_socket_send(socket, data):
  _require_emulated_socket(socket)
  _require_string(data)



def allow_args_emulated_socket_recv(socket, bytes):
  _require_emulated_socket(socket)
  _require_integer(bytes)



SOCKET_OBJECT_WRAPPER_INFO = {
  'close' :
      {'target_func' : emulcomm.emulated_socket.close,
       'arg_checking_func' : allow_args_emulated_socket,
       'return_checking_func' : allow_return_bool},

  'recv' :
      {'target_func' : emulcomm.emulated_socket.recv,
       'arg_checking_func' : allow_args_emulated_socket_recv,
       'return_checking_func' : allow_return_string},
       
  'send' :
      {'target_func' : emulcomm.emulated_socket.send,
       'arg_checking_func' : allow_args_emulated_socket_send,
       'return_checking_func' : allow_return_integer},
  
  # Armon: Add the willblock() call. Takes no args, and returns a bool tuple with 2 entries.
  'willblock' :
      {'target_func' : emulcomm.emulated_socket.willblock,
       'arg_checking_func' : allow_args_emulated_socket,
       'return_checking_func' : allow_return_two_bools_tuple},

}





def _require_lock_object(lockobj):
  # The type(lockobj) is thread.lock, but there is no such thing. So, we use
  # 'isinstance()' here instead of 'is'.
  if not isinstance(lockobj, thread.LockType):
    raise NamespaceRequirementError



def allow_args_lock_acquire(lock, blocking=1):
  _require_lock_object(lock)
  _require_bool_or_integer(blocking)



def allow_args_lock_release(lock):
  _require_lock_object(lock)



LOCK_OBJECT_WRAPPER_INFO = {
  'acquire' :
      # A string for the target_func indicates a function by this name on the
      # instance rather is what should be wrapped.
      {'target_func' : 'acquire',
       'arg_checking_func' : allow_args_lock_acquire,
       'return_checking_func' : allow_return_bool},

  'release' :
      # A string for the target_func indicates a function by this name on the
      # instance rather is what should be wrapped.
      {'target_func' : 'release',
       'arg_checking_func' : allow_args_lock_release,
       'return_checking_func' : allow_return_none},
}

def _require_virtual_namespace_object(virt):
  if not isinstance(virt, virtual_namespace.VirtualNamespace):
    raise NamespaceRequirementError

def allow_args_virtual_namespace_eval(virt, context):
  _require_virtual_namespace_object(virt)
  _require_dict_or_safedict(context)

def allow_return_safedict(context):
  _require_safedict(context)


VIRTUAL_NAMESPACE_OBJECT_WRAPPER_INFO = {
  # Evaluate must take a dict or SafeDict, and can
  # only return a SafeDict. We must _not_ copy the
  # dict since that will screw up the references in the dict.
  'evaluate' :
    {
      'target_func' : 'evaluate',
      'arg_checking_func' : allow_args_virtual_namespace_eval,
      'return_checking_func' : allow_return_safedict
    }
}


##############################################################################
# The classes we define from which actual wrappers are instantiated.
##############################################################################

class NamespaceViolationError(Exception):
  """
  This is the exception that will be raised to user code if there is any
  violation of the namespace rules, including illegal arguments and illegal
  return values. Note that user code can't catch this by name but they can
  catch it by catching all exceptions.
  """





class NamespaceObjectWrapper(object):
  """
  Instances of this class are used to wrap handles and objects returned by
  api functions to the user code.
  
  The methods that can be called on these instances are mostly limited to
  what is in the allowed_functions_dict passed to the constructor. The
  exception is that a simple __repr__() is defined as well as an __iter__()
  and next(). However, instances won't really be iterable unless a next()
  method is defined in the allowed_functions_dict.
  """

  def __init__(self, wrapped_type_name, wrapped_object, allowed_functions_dict):
    """
    <Purpose>
      Constructor
    <Arguments>
      self
      wrapped_type_name
        The name (a string) of what type of wrapped object. For example,
        this could be "timerhandle".
      wrapped_object
        The actual object to be wrapped.
      allowed_functions_dict
        A dictionary of the allowed methods that can be called on the object.
        The keys should be the names of the methods, the values are the
        wrapped functions that will be called.
    """
    # Only one underscore at the front so python doesn't do its own mangling
    # of the name. We're not trying to keep this private in the private class
    # variable sense of python where nothing is really private, instead we just
    # want a double-underscore in there as extra protection against untrusted
    # code being able to access the values.
    self._wrapped__type_name = wrapped_type_name
    self._wrapped__object = wrapped_object
    self._wrapped__allowed_functions_dict = allowed_functions_dict
    

    
  def __getattr__(self, name):
    """
    When a method is called on an instance, we look for the method in the
    allowed_functions_dict that was provided to the constructor. If there
    is such a method in there, we return a function that will properly
    invoke the method with the correct 'self' as the first argument.
    """
    if name in self._wrapped__allowed_functions_dict:
      wrapped_func = self._wrapped__allowed_functions_dict[name]
      
      def __do_func_call(*args, **kwargs):
        return wrapped_func(self._wrapped__object, *args, **kwargs)
      
      return __do_func_call
    
    else:
      # This is the standard way of handling "it doesn't exist as far as we
      # are concerned" in __getattr__() methods.
      raise AttributeError, name



  def __iter__(self):
    """
    We provide __iter__() as part of the class rather than through __getattr__
    because python won't look for the attribute in the object to determine if
    the object is iterable, instead it will look directly at the class the
    object is an instance of. See the docstring for next() for more info.
    """
    return self



  def next(self):
    """
    We provide next() as part of the class rather than through __getattr__
    because python won't look for the attribute in the object to determine if
    the object is iterable, instead it will look directly at the class the
    object is an instance of. We don't want everything that is wrapped to
    be considered iterable, though, so we return a TypeError if this gets
    called but there isn't a wrapped next() method.
    """
    if "next" in self._wrapped__allowed_functions_dict:
      return self._wrapped__allowed_functions_dict["next"](self._wrapped__object)
      
    raise TypeError("You tried to iterate a non-iterator of type " + str(type(self._wrapped__object)))



  def __repr__(self):
    return "<Namespace wrapped " + self._wrapped__type_name + ": " + repr(self._wrapped__object) + ">"



  def __hash__(self):
    # this is done because on some versions of Python, objects like this
    # aren't hashable (#950), we want to make this consistent...
    raise AttributeError("emulated_socket instance has no attribute '__hash__'")



  def __eq__(self, other):
    """In addition to __hash__, this is necessary for use as dictionary keys."""
    # since this isn't hashable, it's only equal if it's the same...
    return self is other



  def __ne__(self, other):
    """
    It's good for consistency to define __ne__ if one is defining __eq__
    """
    return self is not other




class NamespaceAPIFunctionWrapper(object):
  """
  Instances of this class exist solely to provide function wrapping. This is
  done by creating an instance of the class and then making available the
  instance's wrapped_function() method to any code that should only be allowed
  to call the wrapped version of the function.
  """

  def _handle_violation(self, message):
    """
    <Purpose>
      Perform necessary actions for when we detect some form of violation of
      the namespace.
    <Arguments>
      self
      message
        The message (a string) to be included with any raised exception or
        logged information.
    <Exception>
      NamespaceViolationError
        Raised always. Right now that's the purpose of this function.
    <Side Effects>
      None
    <Returns>
      None
    """
    raise NamespaceViolationError("Namespace violation: " + message)



  def _copy(self, obj, objectmap=None):
    """
    <Purpose>
      Create a deep copy of an object without using the python 'copy' module.
      Using copy.deepcopy() doesn't work because builtins like id and hasattr
      aren't available when this is called.
    <Arguments>
      self
      obj
        The object to make a deep copy of.
      objectmap
        A mapping between original objects and the corresponding copy. This is
        used to handle circular references.
    <Exceptions>
      TypeError
        If an object is encountered that we don't know how to make a copy of.
      NamespaceViolationError
        If an unexpected error occurs while copying. This isn't the greatest
        solution, but in general the idea is we just need to abort the wrapped
        function call.
    <Side Effects>
      A new reference is created to every non-simple type of object. That is,
      everything except objects of type str, unicode, int, etc.
    <Returns>
      The deep copy of obj with circular/recursive references preserved.
    """
    try:
      # If this is a top-level call to _copy, create a new objectmap for use
      # by recursive calls to _copy.
      if objectmap is None:
        objectmap = {}
      # If this is a circular reference, use the copy we already made.
      elif _saved_id(obj) in objectmap:
        return objectmap[_saved_id(obj)]
      
      # types.InstanceType is included because the user can provide an instance
      # of a class of their own in the list of callback args to settimer.
      if _is_in(type(obj), [str, unicode, int, long, float, complex, bool, frozenset,
                            types.NoneType, types.FunctionType, types.LambdaType,
                            types.MethodType, types.InstanceType]):
        return obj

      elif type(obj) is list:
        temp_list = []
        # Need to save this in the objectmap before recursing because lists
        # might have circular references.
        objectmap[_saved_id(obj)] = temp_list
        
        for item in obj:
          temp_list.append(self._copy(item, objectmap))
          
        return temp_list

      elif type(obj) is tuple:
        temp_list = []

        for item in obj:
          temp_list.append(self._copy(item, objectmap))
          
        # I'm not 100% confident on my reasoning here, so feel free to point
        # out where I'm wrong: There's no way for a tuple to directly contain
        # a circular reference to itself. Instead, it has to contain, for
        # example, a dict which has the same tuple as a value. In that
        # situation, we can avoid infinite recursion and properly maintain
        # circular references in our copies by checking the objectmap right
        # after we do the copy of each item in the tuple. The existence of the
        # dictionary would keep the recursion from being infinite because those
        # are properly handled. That just leaves making sure we end up with
        # only one copy of the tuple. We do that here by checking to see if we
        # just made a copy as a result of copying the items above. If so, we
        # return the one that's already been made.
        if _saved_id(obj) in objectmap:
          return objectmap[_saved_id(obj)]
        
        retval = tuple(temp_list)
        objectmap[_saved_id(obj)] = retval
        return retval
    
      elif type(obj) is set:
        temp_list = []
        # We can't just store this list object in the objectmap because it isn't
        # a set yet. If it's possible to have a set contain a reference to
        # itself, this could result in infinite recursion. However, sets can
        # only contain hashable items so I believe this can't happen.

        for item in obj:
          temp_list.append(self._copy(item, objectmap))
        
        retval = set(temp_list)
        objectmap[_saved_id(obj)] = retval
        return retval
        
      elif type(obj) is dict:
        temp_dict = {}
        # Need to save this in the objectmap before recursing because dicts
        # might have circular references.
        objectmap[_saved_id(obj)] = temp_dict
        
        for key, value in obj.items():
          temp_key = self._copy(key, objectmap)
          temp_dict[temp_key] = self._copy(value, objectmap)
          
        return temp_dict
      
      # We don't copy certain objects. This is because copying an emulated file
      # object, for example, will cause the destructor of the original one to
      # be invoked, which will close the actual underlying file. As the object
      # is wrapped and the client does not have access to it, it's safe to not
      # wrap it.
      elif isinstance(obj, (NamespaceObjectWrapper, emulfile.emulated_file,
                            emulcomm.emulated_socket, thread.LockType,
                            virtual_namespace.VirtualNamespace)):
        return obj
      
      else:
        raise TypeError("_copy is not implemented for objects of type " + str(type(obj)))
      
    except Exception, e:
      self._handle_violation("_copy failed on " + str(obj) + " with message " + str(e))



  def _check_arguments(self, *args, **kwargs):
    """
    <Purpose>
      Check the arguments against the arg_checking_func provided to the
      constructor.
    <Arguments>
      self
      *args
      **kwargs
        The arguments that will ultimately be passed to the wrapped function.
    <Exceptions>
      TypeError
        If the arguments aren't valid. That is, if they fail the arg checking.
    <Side Effects>
      None
    <Returns>
      None
    """

    try:
      self.__arg_checking_func(*args, **kwargs)

    except NamespaceRequirementError, e:
      if type(self.__target_func) is str:
        name = self.__target_func
      else:
        name = self.__target_func.__name__
      raise TypeError("Function '" + name + "' called with incorrect arguments. " + 
                      str(e) + " Arguments were args:" + str(args) + ", kwargs:" + str(kwargs))
    # We catch a TypeError as some of the argument checking functions don't
    # accept variable args, so python will raise a TypeError if the correct
    # number of args/kwargs hasn't been passed. We don't show the exception
    # string in this case as it will name the argument checking function,
    # which is bound to confuse the user. Of course, confusion will result
    # if we have a bug in our code that is raising a TypeError.
    except TypeError:
      if type(self.__target_func) is str:
        name = self.__target_func
      else:
        name = self.__target_func.__name__
      raise TypeError("Function '" + name + "' called with incorrect arguments. " + 
                      " Arguments were args:" + str(args) + ", kwargs:" + str(kwargs))



  def _check_return_value(self, retval):
    """
    <Purpose>
      Check the return value against the return_checking_func provided to the
      constructor.
    <Arguments>
      self
      retval
        The return value that will ultimately be returned to the calling code
        if it is acceptable.
    <Exceptions>
      NamespaceViolationError
        If the return value isn't acceptable.
    <Side Effects>
      None
    <Returns>
      None
    """

    try:
      self.__return_checking_func(retval)
    except NamespaceRequirementError, e:
      if type(self.__target_func) is str:
        name = self.__target_func
      else:
        name = self.__target_func.__name__
      self._handle_violation("Function '" + name + "' returned with unallowed return type " + 
                             str(type(retval)) + " : " + str(e))



  def _check_raised_exception(self, raised_exception):
    """
    <Purpose>
      Check a raised exceptin against the exception_checking_func provided to
      the constructor.
    <Arguments>
      self
      raised_exception
        The exception that will ultimately be raised to the calling code if it
        is acceptable.
    <Exceptions>
      NamespaceViolationError
        If the exception isn't allowed.
    <Side Effects>
      None
    <Returns>
      None
    """

    try:
      self.__exception_checking_func(raised_exception)
    except NamespaceRequirementError:
      # We include the exception message because it might be a huge pain to
      # debug an error in our code without this.
      # TODO: this will lose the traceback info of the original exception.
      self._handle_violation("Exception of type " + str(type(raised_exception)) + 
                             "is not an allowed exception type. " + 
                             "Exception message was: " + str(raised_exception))



  def __init__(self, func_dict):
    """
    <Purpose>
      Constructor.
    <Arguments>
      self
      func_dict
        A dictionary whose with the following keys whose values are the
        corresponding funcion:
          target_func (required) -- a function or a string of the name
            of the method on the underlying object.
          arg_checking_func (required)
          return_checking_func (required)
          exception_checking_func (optional)
          arg_wrapping_func (optional)
          arg_unwrapping_func (optional)
          return_wrapping_func (optional)
    <Exceptions>
      None
    <Side Effects>
      None
    <Returns>
      None
    """

    # Required in func_dict.    
    self.__target_func = func_dict["target_func"]
    self.__arg_checking_func = func_dict["arg_checking_func"]
    self.__return_checking_func = func_dict["return_checking_func"]

    # Optional in func_dict.
    self.__exception_checking_func = func_dict.get("exception_checking_func", allow_all)
    self.__arg_wrapping_func = func_dict.get("arg_wrapping_func", None)
    self.__arg_unwrapping_func = func_dict.get("arg_unwrapping_func", None)
    self.__return_wrapping_func = func_dict.get("return_wrapping_func", None)

    # Make sure that the __target_func really is a function or a string
    # indicating a function by that name on the underlying object should
    # be called.
    if not _saved_callable(self.__target_func) and type(self.__target_func) is not str:
      raise TypeError("The target_func was neither callable nor a string when " + 
                      "constructing a namespace-wrapped function. The object " + 
                      "used for target_func was: " + repr(self.__target_func))



  def wrapped_function(self, *args, **kwargs):
    """
    <Purpose>
      Act as the function that is wrapped but perform all required sanitization
      and checking of data that goes into and comes out of the underlying
      function.
    <Arguments>
      self
      *args
      **kwargs
        The arguments to the underlying function.
    <Exceptions>
      NamespaceViolationError
        If some aspect of the arguments or function call is not allowed.
      Anything else that the underlying function may raise.
    <Side Effects>
      Anything that the underyling function may do.
    <Returns>
      Anything that the underlying function may return.
    """

    # Copy first, then check.
    args = self._copy(args)
    kwargs = self._copy(kwargs)
    self._check_arguments(*args, **kwargs)

    if self.__arg_wrapping_func is not None:
      args, kwargs = self.__arg_wrapping_func(*args, **kwargs)

    if self.__arg_unwrapping_func is not None:
      args, kwargs = self.__arg_unwrapping_func(*args, **kwargs)

    try:
      # If it's a string rather than a function, then this is our convention
      # for indicating that we want to wrap the function of this particular
      # object. We use this if the function to wrap isn't available without
      # having the object around, such as with real lock objects.
      if type(self.__target_func) is str:
        func_to_call = _saved_getattr(args[0], self.__target_func)
        # The "self" argument will be passed implicitly by python, so we remove
        # it from the args we pass to the function.
        args_without_self = args[1:]
        retval = func_to_call(*args_without_self, **kwargs)
      else:
        retval = self.__target_func(*args, **kwargs)
      
    except Exception, e:
      self._check_raised_exception(e)
      
      # Armon: Do a normal "raise" rather than "raise e" so that the traceback
      # information is preserved. If we are in nested VirtualNamespace's we don't
      # want to reduce the traceback to only the lowest module on the stack.
      raise

    # Copy first, then check.
    retval = self._copy(retval)
    self._check_return_value(retval)
    
    if self.__return_wrapping_func is not None:
      retval = self.__return_wrapping_func(retval)

    return retval
