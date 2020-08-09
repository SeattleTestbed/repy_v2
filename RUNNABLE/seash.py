""" 
Author: Justin Cappos
Edited: Alan Loh

Module: A shell for Seattle called seash (pronounced see-SHH).   It's not meant
        to be the perfect shell, but it should be good enough for v0.1

Start date: September 18th, 2008

This is an example experiment manager for Seattle.   It allows a user to 
locate vessels they control and manage those vessels.

The design goals of this version are to be secure, simple, and reliable (in 
that order).   

Note: I've written this assuming that repy <-> python integration is perfect
and transparent (minus the bit of mess that fixes this).   As a result this
code may change significantly in the future.


Editor's Note: A large portion of seash's code has been separated into
different files. The only code remaining is the command loop that handles the 
user's input and the exception handling.

Command functions have been moved to command_callbacks.py. 

Helper functions and functions that operate on a target have been moved to 
seash_helper.py.

The newly implemented command dictionary, input parsing, and command dispatching 
have been moved to seash_dictionary.py.

Certain global variables are now kept track in seash_global_variables.py.

Besides the restructuring, the main change that has been made on seash is 
command input are now parsed according to the command dictionary. In addition,
with a structured database of sorts for commands, it should now be easier to 
implement new functions into seash as long as the correct format is followed in
implementing new commands.
"""


# Let's make sure the version of python is supported
import checkpythonversion
checkpythonversion.ensure_python_version_is_supported()

# Warnings are turned on to display the tab completion warning
import warnings
warnings.simplefilter("default")

# simple client.   A better test client (but nothing like what a real client
# would be)

# Restores the original python built-in type() to certain built-in libraries
# as repyportability destroys it.

# Needed for parsing user commands and executing command functions
import seash_dictionary

# We need to expose the readline object file to OSX because the default object
# file for Python 2.7 on OSX is not compatible with our tab completion module.
import os
import sys

# Only rename if we're running on OSX
rename_readline_so_file = sys.platform == 'darwin'
HIDDEN_READLINE_SO_FN = 'readline.so.mac'
EXPOSED_READLINE_SO_FN = 'readline.so'

# Make sure we don't overwrite an existing readline.so if it exists.
# We need to do this because os.rename() doesn't raise any errors
# if the destination file already exists.
if (rename_readline_so_file and 
    EXPOSED_READLINE_SO_FN not in os.listdir('.')):
  try:
    os.rename(HIDDEN_READLINE_SO_FN, EXPOSED_READLINE_SO_FN)
  except OSError:
    # There was a problem reading readline.so.mac
    rename_readline_so_file = False

tabcompletion = True
try:
  try:
    # Required for windows tab-completion. 
    # This is the readline module provided by pyreadline 1.7.1.
    # http://pypi.python.org/pypi/pyreadline
    import readline_windows as readline
  except ImportError:
    # This error occurs when trying to import win_readline on mac/linux.
    # We use the default readline module for mac/linux.
    import readline
  import tab_completer
except ImportError:
  tabcompletion = False
  
# Don't hide mac readline.so if we didn't expose it
if rename_readline_so_file:
  os.rename(EXPOSED_READLINE_SO_FN, HIDDEN_READLINE_SO_FN)

# Used for re-enabling modules on the last run
import seash_modules

# To be able to catch certain exceptions thrown throughout the program
import seash_exceptions

import seash_helper

import traceback

import os.path    # fix path names when doing upload, loadkeys, etc.




def command_loop(test_command_list):
  
  # If a test command list is passed, filter the tab completion warning
  if test_command_list:
    warnings.filterwarnings("ignore", "Auto tab completion is off, because it is not available on your operating system.",
                            ImportWarning)


  # Things that may be set herein and used in later commands.
  # Contains the local variables of the original command loop.
  # Keeps track of the user's state in seash. Referenced 
  # during command executions by the command_parser.
  environment_dict = {
    'host': None, 
    'port': None, 
    'expnum': None,
    'filename': None,
    'cmdargs': None,
    'defaulttarget': None,
    'defaultkeyname': None,
    'currenttarget': None,
    'currentkeyname': None,
    'autosave': False,
    'handleinfo': {},
    'showparse': True,
    }

  

  # Set up the tab completion environment (Added by Danny Y. Huang)
  if tabcompletion:
    # Initializes seash's tab completer
    completer = tab_completer.Completer()
    readline.parse_and_bind("tab: complete")
    # Determines when a new tab complete instance should be initialized,
    # which, in this case, is never, so the tab completer will always take
    # the entire user's string into account
    readline.set_completer_delims("")
    # Sets the completer function that readline will utilize
    readline.set_completer(completer.complete)
  else:
    warnings.warn("Auto tab completion is off, because it is not available on your operating system.",ImportWarning)


  # If passed a list of commands, do not prompt for user input
  if test_command_list:
    seash_helper.update_time()
    # Iterates through test_command_list in sequential order
    for command_strings in test_command_list:
      # Saving state after each command? (Added by Danny Y. Huang)
      if environment_dict['autosave'] and environment_dict['defaultkeyname']:
        try:
          # State is saved in file "autosave_username", so that user knows which
          # RSA private key to use to reload the state.
          autosavefn = "autosave_" + str(environment_dict['defaultkeyname'])
          seash_helper.savestate(autosavefn, 
              environment_dict['handleinfo'], environment_dict['host'], 
              environment_dict['port'], environment_dict['expnum'], 
              environment_dict['filename'], environment_dict['cmdargs'], 
              environment_dict['defaulttarget'], environment_dict['defaultkeyname'], 
              environment_dict['autosave'], environment_dict['defaultkeyname'])
        except Exception, error:
          raise seash_exceptions.UserError("There is an error in autosave: '" + 
              str(error) + "'. You can turn off autosave using the command 'set autosave off'.")

      # Returns the dictionary of dictionaries that correspond to the
      # command string
      cmd_input = seash_dictionary.parse_command(command_strings, display_parsed_result=environment_dict['showparse'])
      
      # by default, use the target specified in the prompt
      environment_dict['currenttarget'] = environment_dict['defaulttarget']
      
      # by default, use the identity specified in the prompt
      environment_dict['currentkeyname'] = environment_dict['defaultkeyname']

      # calls the command_dispatch method of seash_dictionary to execute the callback
      # method associated with the command the user inputed
      seash_dictionary.command_dispatch(cmd_input, environment_dict)



  # Otherwise launch into command loop, exit via return
  else:
    while True:
      try:
        if tabcompletion:
          # Updates the list of variable values in the tab complete class
          completer.set_target_list()
          completer.set_keyname_list()
          
        # Saving state after each command? (Added by Danny Y. Huang)
        if environment_dict['autosave'] and environment_dict['defaultkeyname']:
          try:
            # State is saved in file "autosave_username", so that user knows which
            # RSA private key to use to reload the state.
            autosavefn = "autosave_" + str(environment_dict['defaultkeyname'])
            seash_helper.savestate(autosavefn, environment_dict['handleinfo'], environment_dict['host'], 
                                   environment_dict['port'], environment_dict['expnum'], 
                                   environment_dict['filename'], environment_dict['cmdargs'], 
                                   environment_dict['defaulttarget'], environment_dict['defaultkeyname'], 
                                   environment_dict['autosave'], environment_dict['defaultkeyname'])
          except Exception, error:
            raise seash_exceptions.UserError("There is an error in autosave: '" + str(error) + "'. You can turn off autosave using the command 'set autosave off'.")


        prompt = ''
        if environment_dict['defaultkeyname']:
          prompt = seash_helper.fit_string(environment_dict['defaultkeyname'],20)+"@"

        # display the thing they are acting on in their prompt (if applicable)
        if environment_dict['defaulttarget']:
          prompt = prompt + seash_helper.fit_string(environment_dict['defaulttarget'],20)

        prompt = prompt + " !> "
        # the prompt should look like: justin@good !> 
        
        # get the user input
        userinput = raw_input(prompt)
        
        # allows commenting
        comment_index = userinput.find('#')

        # throw away anything after (and including) the '#'
        if comment_index != -1:
          userinput = userinput[0:comment_index]

        # drop any leading or trailing whitespace
        userinput = userinput.strip()

        # if it's an empty line, continue...
        if len(userinput)==0:
          continue
      
        # Returns the dictionary of dictionaries that correspond to the
        # command the user inputted
        cmd_input = seash_dictionary.parse_command(userinput, display_parsed_result=environment_dict['showparse'])
      
      
        # by default, use the target specified in the prompt
        environment_dict['currenttarget'] = environment_dict['defaulttarget']
        
        # by default, use the identity specified in the prompt
        environment_dict['currentkeyname'] = environment_dict['defaultkeyname']

        # calls the command_dispatch method of seash_dictionary to execute the callback
        # method associated with the command the user inputed
        seash_dictionary.command_dispatch(cmd_input, environment_dict)


 

# handle errors
      except KeyboardInterrupt:
        # print or else their prompt will be indented
        print
        # Make sure the user understands why we exited
        print 'Exiting due to user interrupt'
        return
      except EOFError:
        # print or else their prompt will be indented
        print
        # Make sure the user understands why we exited
        print 'Exiting due to EOF (end-of-file) keystroke'
        return

      except seash_exceptions.ParseError, error_detail:
        print 'Invalid command input:', error_detail
      except seash_exceptions.DispatchError, error_detail:
        print error_detail
      except seash_exceptions.UserError, error_detail: 
        print error_detail
      except SystemExit:
        # exits command loop
        return
      except:
        traceback.print_exc()
      
  
  
if __name__=='__main__':
  seash_helper.update_time()
  seash_modules.enable_modules_from_last_session(seash_dictionary.seashcommanddict)
  
  # For general usage, empty list is passed to prompt for user input
  command_loop([])
