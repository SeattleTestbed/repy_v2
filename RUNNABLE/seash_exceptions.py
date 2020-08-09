"""
Author: Alan Loh

Module: A library to hold the definitions of common 
        seash exceptions and errors.

To avoid declaring or inheriting the same exception 
definitions from other files, declare all new exceptions
and errors here for easier accessibility by other files.
"""

# Base class for module-related errors/exceptions.
class ModuleError(Exception):
  pass

# There is a conflict between two modules.
# The string passed in should be the conflicting command.
class ModuleConflictError(ModuleError):
  pass

# Used by module system for errors in importing modules
class ModuleImportError(ModuleError):
  pass


# Used by command parser for errors in reading commands
class DispatchError(Exception):
  pass

# Used by the command parser for invalid command inputs
class ParseError(Exception):
  pass

# Use this to signal an error we want to print...
class UserError(Exception):
  """This indicates the user typed an incorrect command"""
  pass

# Use this to signal an error during initializing module.
class InitializeError(Exception):
  pass