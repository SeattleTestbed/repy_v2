"""
Author: Alan Loh, Danny Huang

Module: A class that allows for tab completion of command words and certain user
        arguments in the seash command prompt. Available completions are 
        determined by the seash command dictionary.

Upon initialization of the seash command prompt, a Completer object is
initialized and maintains a copy of the seash command dictionary. At the beginning
of each command loop, the Completer will update its arguments list for the
purpose of tab completion for target IDs and loaded keynames.

When the user double tabs, seash passes the command inputted thus far to the tab
completer. Tab completion first determines where in the command dictionary has
the user inputted up to thus far, and a list of possible command completions is 
built based on the children of the last command string inputted. A
list of commands will be returned if there are multiple possible completions, or
the tab completer will automatically complete the user input in the command
prompt if there's only one completion available.

There is a slight issue of inefficiency in that each time tab completion is
called with a new user prefix, the tab completer will always include the user's
prefix in addition to the completed word as part of the returned completion.
Since seash commands are generally short in length, this is not an issue yet,
but there is still room for improvement.

This only applies for operating systems that supports readline. This particular
version's file name completer is compatible only with systems that uses '/' in
their directory paths.
"""

import os
import os.path
import seash_dictionary
import seash_global_variables
import seash_modules

class Completer:
  def __init__(self):
    self._prefix = None
    # Retrieves a copy of seash's command dictionary for reference
    self.commanddict = seash_dictionary.return_command_dictionary()




  # Creates and updates the list of targets and groups for tab completion
  def set_target_list(self):
    self.targetList = seash_global_variables.targets.keys()[:]




  # Creates and updates the list of available key names for tab completion
  def set_keyname_list(self):
    self.keynameList = seash_global_variables.keys.keys()



  # Returns the path from a given prefix, by extracting the string up to the
  # last forward slash in the prefix. If no forward slash is found, returns an
  # empty string.
  def _getpath(self, prefix):

    slashpos = prefix.rfind("/")
    currentpath = ""
    if slashpos > -1:
      currentpath = prefix[0 : slashpos+1]

    return currentpath



  # Returns the file name, or a part of the file name, from a given prefix, by
  # extracting the string after the last forward slash in the prefix. If no
  # forward slash is found, returns an empty string.
  def _getfilename(self, prefix):

    # Find the last occurrence of the slash (if any), as it separates the path
    # and the file name.
    slashpos = prefix.rfind("/")
    filename = ""

    # If slash exists and there are characters after the last slash, then the
    # file name is whatever that follows the last slash.
    if slashpos > -1 and slashpos+1 <= len(prefix)-1:
      filename = prefix[slashpos+1:]

    # If no slash is found, then we assume that the entire user input is the
    # prefix of a file name because it does not contain a directory
    elif slashpos == -1:
      filename = prefix

    # If both cases fail, then the entire user input is the name of a
    # directory. Thus, we return the file name as an empty string.
    return filename




  # Returns a list of file names that start with the given prefix.
  def _listfiles(self, prefix):
    
    # Find the directory specified by the prefix
    currentpath = self._getpath(prefix)
    if not currentpath:
      currentpath = "./"
    filelist = []

    # Attempt to list files from the given directory
    try:
      currentpath = os.path.expanduser(currentpath)
      filelist = os.listdir(currentpath)

    # In the case an exception occurs, return filelist anyway as it will be empty
    finally:
      return filelist




  # Iterates through the command dictionary and returns the list of children of the last valid 
  # command in the passed string list
  def _get_all_commands(self, input_list):
    # The iterator that will iterate through the command dictionary based on what
    # the user has inputted thus far
    dict_iterator = self.commanddict

    # The list of command completions that will be built throughout the method
    completion_list = []

    # Reference to keep track of the last string the user inputted
    last_string = ""

    # Determines if the last string the user inputted was incomplete
    incomplete_string = False


    # Iterate through the input list to determine current path down the command dictionaries
    for commands in input_list:
      last_string = commands

      if commands in dict_iterator.keys():
        dict_iterator = dict_iterator[commands]['children']


      # Test the possibility of an user argument in the input list by first
      # seeing if the command exists as one of the child's of the current key,
      # and, if applicable, the user's input corresponds to one of the possibilities
      # in the list of possible argument names
      elif '[TARGET]' in dict_iterator.keys() and commands in self.targetList:
        dict_iterator = dict_iterator['[TARGET]']['children']
      elif '[GROUP]' in dict_iterator.keys() and commands in self.targetList:
        dict_iterator = dict_iterator['[GROUP]']['children']
      elif '[KEYNAME]' in dict_iterator.keys() and commands in self.keynameList:
        dict_iterator = dict_iterator['[KEYNAME]']['children']
      elif '[FILENAME]' in dict_iterator.keys() and self._getfilename(commands) in self._listfiles(commands):
        dict_iterator = dict_iterator['[FILENAME]']['children']
      elif '[ARGUMENT]' in dict_iterator.keys():
        dict_iterator = dict_iterator['[ARGUMENT]']['children']


      # Otherwise, if it's not an user argument nor is it a command word, set
      # incomplete_string to be true
      else:
        incomplete_string = True


    # Reconstructs the user's input up to the last string if it's incomplete,
    # or just reconstructs the user's input entirely if that's not the case
    if incomplete_string:
      user_prefix = " ".join(input_list[:input_list.index(last_string)])
    else:
      user_prefix = " ".join(input_list[:])


    # Creates a list of all the possible command completions 
    for child in dict_iterator.keys():

      # User argument completion. All argument key names begins with '['
      if child.startswith('['):
        # Tab completer will not differentiate between a group from a target
        if child == '[TARGET]' or child == '[GROUP]':
          for targets in self.targetList:
            completed_command = user_prefix + ' ' + targets
            completion_list.append(completed_command.strip() + ' ')
      
        elif child == '[KEYNAME]':
          for keynames in self.keynameList:
            completed_command = user_prefix + ' ' + keynames
            completion_list.append(completed_command.strip() + ' ')
      
        elif child == '[FILENAME]':
          # Find the directory specified by the user's last inputted string
          currentpath = self._getpath(last_string)
          if not currentpath:
            currentpath = "./"

          # Finds the full path of the user's given directory in case a '~' was given
          currentpath = os.path.expanduser(currentpath)

          for filenames in self._listfiles(last_string):
            dirfile = os.path.join(currentpath, filenames)
            completed_command = user_prefix + ' ' + self._getpath(last_string) + filenames

            # For directory names, adds a forward slash at the end of the tab completion
            # For file names, adds a space at the end of the tab completion
            if os.path.isdir(dirfile):
              completion_list.append(completed_command.strip() + '/')
            else:
              completion_list.append(completed_command.strip() + ' ')
      

      # Command word completion
      else:
        completed_command = user_prefix + ' ' + child
        completion_list.append(completed_command.strip() + ' ')

    return completion_list





  # The actual tab completion method
  def complete(self, prefix, index):
    # If the passed prefix is different than the previously passed prefix,
    # then a new list of possible completions needs to be constructed corresponding
    # to the new prefix
    if prefix != self._prefix:
      self._matching_words = []

      # split the user input into a list of strings
      input_list = prefix.split()
      # Retrieves the list of children of the current command dictionary based on
      # the current input of the user
      self._words = self._get_all_commands(input_list)
      
      # Retrieves the list of words from modules based on the current input of 
      # the user
      self._words += seash_modules.tab_complete(input_list)
      
      for word in self._words:
        if word.startswith(prefix):
          self._matching_words.append(word)

      # updates prefix to determine when a new completion list needs to be made
      self._prefix = prefix
    

    try:
      return self._matching_words[index]
    except IndexError:
      return None
