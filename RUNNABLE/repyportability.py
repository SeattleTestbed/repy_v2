
import __builtin__

# I'm importing these so I can neuter the calls so that they aren't 
# restricted...

import os
import sys
import safe
import nanny
import emulfile
import emulmisc
import namespace
import nonportable
import virtual_namespace

# WTF!?! repyportability uses repyhelper to import dylink!?!
import repyhelper

# JAC: Save the calls in case I want to restore them.   This is useful if 
# repy ends up wanting to use either repyportability or repyhelper...
# This is also useful if a user wants to enforce restrictions on the repy
# code they import via repyhelper (they must use 
# restrictions.init_restriction_tables(filename) as well)...
oldrestrictioncalls = {}
oldrestrictioncalls['nanny.tattle_quantity'] = nanny.tattle_quantity
oldrestrictioncalls['nanny.tattle_add_item'] = nanny.tattle_add_item
oldrestrictioncalls['nanny.tattle_remove_item'] = nanny.tattle_remove_item
oldrestrictioncalls['nanny.is_item_allowed'] = nanny.is_item_allowed
oldrestrictioncalls['nanny.get_resource_limit'] = nanny.get_resource_limit
oldrestrictioncalls['nanny._resources_allowed_dict'] = nanny._resources_allowed_dict
oldrestrictioncalls['nanny._resources_consumed_dict'] = nanny._resources_consumed_dict
oldrestrictioncalls['emulfile.assert_is_allowed_filename'] = emulfile._assert_is_allowed_filename


port_list = range(60000, 65000)

default_restrictions = {'loopsend': 100000000.0, 'netrecv': 1000000.0, 'random': 10000.0, 'insockets': 500.0, 'fileread': 10000000.0, 'netsend': 1000000.0, 'connport': set(port_list), 'messport': set(port_list), 'diskused': 10000000000.0, 'filewrite': 10000000.0, 'lograte': 3000000.0, 'filesopened': 500.0, 'looprecv': 100000000.0, 'events': 1000.0, 'memory': 150000000000.0, 'outsockets': 500.0, 'cpu': 1.0, 'threadcpu' : 1.0}


resource_used = {'diskused': 0.0, 'renewable_update_time': {'fileread': 0.0, 'loopsend': 0.0, 'lograte': 0.0, 'netrecv': 0.0, 'random': 0.0, 'filewrite': 0.0, 'looprecv': 0.0, 'netsend': 0.0, 'cpu': 0.0}, 'fileread': 0.0, 'loopsend': 0.0, 'filesopened': set([]), 'lograte': 0.0, 'netrecv': 0.0, 'random': 0.0, 'insockets': set([]), 'filewrite': 0.0, 'looprecv': 0.0, 'events': 0.0, 'messport': set([]), 'memory': 0.0, 'netsend': 0.0, 'connport': set([]), 'outsockets': set([]), 'cpu': 0.0, 'threadcpu' : 1.0}

def _do_nothing(*args):
  pass

def _always_true(*args):
  return True


# Overwrite the calls so that I don't have restrictions (the default)
def override_restrictions():
  """
   <Purpose>
      Turns off restrictions.   Resource use will be unmetered after making
      this call.   (note that CPU / memory / disk space will never be metered
      by repyhelper or repyportability)

   <Arguments>
      None.
         
   <Exceptions>
      None.

   <Side Effects>
      Resource use is unmetered / calls are unrestricted.

   <Returns>
      None
  """
  nonportable.get_resources = _do_nothing

  nanny.tattle_quantity = _do_nothing
  nanny.tattle_add_item = _do_nothing
  nanny.tattle_remove_item = _do_nothing
  nanny.is_item_allowed = _always_true
  nanny.get_resource_limit = _do_nothing
  nanny._resources_allowed_dict = default_restrictions
  nanny._resources_consumed_dict = resource_used
  emulfile._assert_is_allowed_filename = _do_nothing
  


# Sets up restrictions for the program
# THIS IS ONLY METERED FOR REPY CALLS AND DOES NOT INCLUDE CPU / MEM / DISK 
# SPACE
def initialize_restrictions(restrictionsfn):
  """
   <Purpose>
      Sets up restrictions.   This allows some resources to be metered 
      despite the use of repyportability / repyhelper.   CPU / memory / disk 
      space will not be metered.   Call restrictions will also be enabled.

   <Arguments>
      restrictionsfn:
        The file name of the restrictions file.
         
   <Exceptions>
      None.

   <Side Effects>
      Enables restrictions.

   <Returns>
      None
  """
  nanny.start_resource_nanny(restrictionsfn)

def enable_restrictions():
  """
   <Purpose>
      Turns on restrictions.   There must have previously been a call to
      initialize_restrictions().  CPU / memory / disk space will not be 
      metered.   Call restrictions will also be enabled.

   <Arguments>
      None.
         
   <Exceptions>
      None.

   <Side Effects>
      Enables call restrictions / resource metering.

   <Returns>
      None
  """
  # JAC: THIS WILL NOT ENABLE CPU / MEMORY / DISK SPACE
  nanny.tattle_quantity = oldrestrictioncalls['nanny.tattle_quantity']
  nanny.tattle_add_item = oldrestrictioncalls['nanny.tattle_add_item'] 
  nanny.tattle_remove_item = oldrestrictioncalls['nanny.tattle_remove_item'] 
  nanny.is_item_allowed = oldrestrictioncalls['nanny.is_item_allowed'] 
  nanny.get_resource_limit = oldrestrictioncalls['nanny.get_resource_limit']
  nanny._resources_allowed_dict = oldrestrictioncalls['nanny._resources_allowed_dict']
  nanny._resources_consumed_dict = oldrestrictioncalls['_resources_consumed_dict']
  emulfile.assert_is_allowed_filename = oldrestrictioncalls['emulfile.assert_is_allowed_filename']
  
# from virtual_namespace import VirtualNamespace
# We need more of the module then just the VirtualNamespace
from virtual_namespace import *
from safe import *
from emulmisc import *
from emulcomm import *
from emulfile import *
from emultimer import *

# Buld the _context and usercontext dicts.
# These will be the functions and variables in the user's namespace (along
# with the builtins allowed by the safe module).
usercontext = {'mycontext':{}}

# Add to the user's namespace wrapped versions of the API functions we make
# available to the untrusted user code.
namespace.wrap_and_insert_api_functions(usercontext)

# Convert the usercontext from a dict to a SafeDict
usercontext = safe.SafeDict(usercontext)

# Allow some introspection by providing a reference to the context
usercontext["_context"] = usercontext
usercontext["getresources"] = nonportable.get_resources
usercontext["createvirtualnamespace"] = virtual_namespace.createvirtualnamespace
usercontext["getlasterror"] = emulmisc.getlasterror
_context = usercontext.copy()

# This is needed because otherwise we're using the old versions of file and
# open.   We should change the names of these functions when we design
# repy 0.2
originalopen = open
originalfile = file
openfile = emulated_open

# file command discontinued in repy V2
#file = emulated_open

# Create a mock copy of getresources()
def getresources():
  return (default_restrictions, resource_used, [])
  
# Needed for ticket #1038.
# `safe._builtin_destroy()` normally removes the ability to call `import`.
# it would be called inside of `createvirtualnamespace()`
# If we didn't do this, we would not be able to call `import` after 
# calling `createvirtualnamespace()`
for builtin_type in dir(__builtin__):
  if builtin_type not in safe._BUILTIN_OK:
    safe._BUILTIN_OK.append(builtin_type)


def initialize_safe_module():
    """
    A helper private function that helps initialize
    the safe module.
    """

    # Allow Import Errors.
    safe._NODE_CLASS_OK.append("Import")

    # needed to allow primitive marshalling to be built
    safe._BUILTIN_OK.append("__import__")
    safe._BUILTIN_OK.append("open")
    safe._BUILTIN_OK.append("eval")


    # Allow all built-ins
    for builtin_type in dir(__builtins__):
      if builtin_type not in safe._BUILTIN_OK:
        safe._BUILTIN_OK.append(builtin_type)
    
    for str_type in dir(__name__):
      if str_type not in safe._STR_OK:
        safe._STR_OK.append(str_type)

    safe.serial_safe_check = _do_nothing
    safe._check_node = _do_nothing


  
# Override by default!
override_restrictions()
initialize_safe_module()




# This function makes the dy_* functions available.
def add_dy_support(_context):
  """
  <Purpose>
    Enable usage of repy's dynamic library linking.  This should only
    be called on the module-level.

  <Arguments>
    _context:
      The context that dylink's functions should be inserted into.

  <Side Effects>
    Public functions from dylink.repy will be inserted into _context.
    _context should be globals() for a module.

  <Exceptions>
    Exception is raised when a module import fails.

  <Returns>
    None
  """
  # Add dylink support
  repyhelper.translate_and_import("dylink.r2py", callfunc = 'initialize')
  
  # The dy_* functions are only added to the namespace after init_dylink is called.
  init_dylink(_context,{})

  original_import_module = _context['dy_import_module']

  def _new_dy_import_module_symbols(module, callfunc="import"):
    # Remember the path we are currently in. We need to change to 
    # this script's dir (assuming it also contains dylink.r2py and 
    # rest of the Repy runtime and libraries) so that dylink is 
    # able to link in code from the runtime.
    # This is required due to Repy safety measures that inhibit 
    # dylink to access files outside of its directory. 
    # Once dylink is done, we return to the previously-current 
    # working dir.
    previous_cwd = os.getcwd()
    repyportability_dir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(repyportability_dir)

    # If we are using repyportability, we want to check all pythonpath for
    # the file we are looking to import.
    COMMON_EXTENSIONS = ["", ".py", ".repy",".py.repy", ".pp", ".r2py"] 
    
    # Check all combination of filepath with file extension and try to import the
    # file if we have found it.
    for pathdir in sys.path:
      possiblefilenamewithpath = os.path.join(pathdir, module)
   
      # If we have found a path, then we can import the module and
      # return so we do not continue to look in other paths.
      if os.path.isfile(possiblefilenamewithpath):
        filenamewithpath = possiblefilenamewithpath
        importedmodule = original_import_module(filenamewithpath, callfunc)
        os.chdir(previous_cwd)
        return importedmodule

    # If we don't find the file, we just call down to dylink, and
    # let it raise the appropriate error.
    try:
      importedmodule = original_import_module(module, callfunc)
      return importedmodule
    except:
      raise
    finally:
      os.chdir(previous_cwd)

  _context['dy_import_module'] = _new_dy_import_module_symbols


  # Make our own `dy_import_module_symbols` and  add it to the context.
  # It is not currently possible to use the real one (details at ticket #1046)
  def _dy_import_module_symbols(module,new_callfunc="import"):
    new_context = _context['dy_import_module'](module, new_callfunc)._context
    # Copy in the new symbols into our namespace.
    for symbol in new_context:  
      if symbol not in _context: # Prevent the imported object from destroying our namespace.
        _context[symbol] = new_context[symbol]


 
  _context['dy_import_module_symbols'] = _dy_import_module_symbols



