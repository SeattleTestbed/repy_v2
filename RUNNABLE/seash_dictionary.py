"""
Author: Alan Loh

Module: A data structure of all the available commands of seash held in a
        dictionary of dictionaries format. Also holds the methods for
        parsing user command input and executing functions corresponding
        to the command.

User input is parsed according to whether or not it follows the structure 
of a command's dictionary and its children.  When parsing a command word, 
it simply checks to see if the user's input string list contains the command word 
at the appropriate index respective to the level of command dictionary currently
being iterated. If it is an user argument, however, it will
simply assign the user's inputted string as the key of the respective
argument's dictionary.

Command input is split by white spaces, so except for the case of arguments 
located at the end of the command string series, the parser will not taken 
into account file names or arguments that are multiple words long. Also, 
because of the way the command callback functions pull out user arguments, 
arguments of similar type need different 'name' field in its command dictionary
to help distinguish one from the other.
"""

# repyportability destroys the built-in type variable, so we need to
# restore the python built-in type function in order for python
# libraries to work.

# The unit tests often import seash_dictionary directly instead of going
# through seash, so let's re-insert here so that we cover as much ground
# as possible..
originaltype = type
#import repyportability # XXX Why is this needed?
import abc
import warnings
abc.type = originaltype
warnings.type = originaltype


# for access to list of targets
import seash_global_variables

import seash_exceptions

import command_callbacks

# Used for module preprocessing of user input
import seash_modules


# Prints the help text of the last command node that has one
# Also lists all sub-commands that follow the command node.
def print_help(input_dict, environment_dict):
  # Iterate through the user command dictionary
  dict_mark = input_dict

  command_string = ""
  cmdgroup = ''

  while dict_mark.keys():
     # Pulls out the current command key word
     command_key = dict_mark.keys()[0]
     if dict_mark[command_key]['name'] == 'display_group':
       cmdgroup = command_key
     else:
       command_string += command_key + ' '

       # If the command's help text isn't an empty string, sets it as the help_text
       # that will be printed out
       if dict_mark[command_key]['help_text'] is not '':
          current_help_text = dict_mark[command_key]['help_text']

     # Iterates into the next dictionary of children commands
     dict_mark = dict_mark[command_key]['children']

  # Remove the 'help' token.
  command_string = command_string.split('help ', 1)[1]

  command_summaries = get_command_summaries(input_dict)
  
  # summary_strings[module] = formatted string for command summary text for all
  #                           commands under that module
  summary_strings = {}
  if command_summaries:
    # cmdgroup can either be a command or a display group.
    # However, if we get to this point, then cmdgroup can never be a command
    # because the command dispatcher will correctly identify it as such.
    # Therefore, if this is not a display group, we should flag it as an error.
    if cmdgroup and not cmdgroup in command_summaries:
      raise seash_exceptions.UserError("'"+cmdgroup+"' is not an enabled command nor a display group.")
    for module in command_summaries[cmdgroup]:
      summary_strings[module] = get_string_from_command_summarylist(command_summaries[cmdgroup][module], command_string)

  # What should be displayed:
  # -- Help text --
  # (help_text that is defined at the command)
  # A target can be either a host:port:vesselname, %ID, or a group name.
  # -- Subcommand list --
  # (Lists the summaries of all subcommands that fall under the display group)
  # add       -- Adds a target (a vessel name or group) to a group.
  # get       -- Acquires vessels from the clearinghouse.
  # release   -- Release vessels from your control
  # show      -- Displays shell state (see 'help show')
  # -- Additional subcommand modifiers --
  # (Lists all additional display groups, if the user did not specify a display group)
  # For more commands, try:
  #   help extended

  print
  print current_help_text.strip()
  print
  
  summary_modules = summary_strings.keys()
  summary_modules.sort()
  for module in summary_modules:
    if not module is None:
      print "Commands from the", module, "module:"
    print summary_strings[module]

  # Display additional cmdgroups if the user did not enter one
  if not cmdgroup:
    # Are there additional keywords?
    additional_cmdgroups = command_summaries.keys()
    # Ignore the default '' keyword.
    if '' in additional_cmdgroups:
      additional_cmdgroups.remove('')
    if None in additional_cmdgroups:
      additional_cmdgroups.remove(None)

    if additional_cmdgroups:
      # List them alphabetically
      additional_cmdgroups.sort()
      print "For more commands, try:"
      command_string = 'help ' + command_string
      for alt_cmdgroup in additional_cmdgroups:
        print "  " + command_string.rstrip(), alt_cmdgroup
      print

"""
Command dictionary entry format:
  '(command key)':{'name':'', 'callback':, 'priority':, 'summary':'', 'example':'', 'help_text':'', 'children':[

'(command key)' - The expected command word the user is suppose to input to
call the command's function. If a certain type of argument is expected, a general
word in all caps should be enclosed within square brackets that signify the type 
of argument needed. For example, '[TARGET]' if a target ID is expected, or 
'[FILENAME]' if the name of a file is needed. Frequently used type includes 
'[TARGET]' for targets, '[KEYNAME]' for loaded keynames, '[FILENAME]' for files,
and '[ARGUMENT]' for everything else, so unless another category of arguments is 
needed, only use those four strings for command keys of arguments in order for 
the parser to work correctly.
 

For general commands like 'browse', however, the key would simply be the same
command word, 'browse'.

In general, the command key should only be a single word from the whole command
string being implemented, and with the exception of arguments that occur at the
end of the command string, no user-inputted arguments should ever contain spaces.


'name':       - The name of the command word. For general commands, it should be 
the same as the command key. For arguments, however, the name should be 
distinguishable from other potential arguments of the same command key to avoid 
conflicts when pulling the user's argument from the input dictionary during 
command execution.


'callback':     - Reference to the command callback function associated with the
command string up to this point. Only command dictionaries that mark a complete 
command string should contain a reference to a callback method. Otherwise, it 
should be set to none. Default location of command callback functions is 
command_callbacks.py.


'priority'      - Gives the command callback function of the dictionary 
containing the key 'priority' the priority of being executed first before 
executing the main function of the command string. It should be implemented and 
assigned True if needed. Otherwise, it should not be added into any other command
dictionary.

An example of how it should work is in the case of 'as [KEYNAME] browse':
A keyname needs to be set before executing 'browse', so the command dictionary of
'[KEYNAME]' has 'priority' in being executed first to set the user's keyname 
before executing 'browse's command function.


'summary'       - A short summary text that should be shown next to the command.
This should be no longer than a sentence if possible. All commands should have a
summary text.


'cmdgroup'- The keyword that should be passed to 'help' to show the summary
text for this command. Commonly used commands that should be shown by default
should have the empty string, or omit this key.


For example, some of the lesser used root commands (join, loadstate, etc.) should
only be shown when the user types 'help extended'. For these commands, the
'cmdgroup' should be set to 'extended'.


'help_text'     - The text that will be outputted whenever a user accesses the
help function for that command. Not every command dictionary needs a help text
associated with it, so it defaults as a blank string, and if none of the command 
dictionaries in the help call holds a help text, it will default at the last 
command dictionary that holds one, namely the dictionary associated with 'help'.


'children'      - The list of command dictionaries that follows the current one.
This will determine the validity of an command input when parsing. Each user
inputted string is verified that it follows one of the potential chains of 
command strings through the series of command dictionaries. Limit only one
argument dictionary per children list to avoid confusion when parsing user
argument input.
 
For example, in the command 'show resources', the children of the command 
dictionary for 'show' will contain the command dictionary 'resources' along with
any other potential command words that can follow 'show'.

"""


seashcommanddict = {
  'on':{
    'name':'on', 'callback':None, 'example': 'target [command]',
    'summary':'Run a command on a target (or changes the default)', 'help_text':"""
on group
on group [command]

Sets the default group for future commands.   Most other commands will only 
operate on the vessels specified in the default group.  The default group is 
listed in the seash command prompt 'identity@group !>'.   The 'on' command can 
also be prepended to another command to set the group for only this command.


Example:

exampleuser@browsegood !> on WAN
exampleuser@WAN !>

exampleuser@browsegood !> on WAN show ip
1.2.3.4
5.6.7.8
exampleuser@browsegood !>
""", 'children':{
      '[TARGET]':{'name':'ontarget', 'callback':command_callbacks.on_target, 'priority':True, 'help_text':'', 'children':{
      }}
  }},


  'as':{
    'name':'as', 'callback':None, 'example':'keyname [command]',
    'summary':'Run a command using an identity (or changes the default)', 'help_text':"""
Sets the default identity for an operation.   The credentials (i.e. public
and private key) for this user are used for the following commands.   
The default identity is listed in the seash command prompt 'identity@group !>'.
The 'as' command can also be prepended to another command to set the identity 
for just this command.

Example:

exampleuser@%all !> as tom
tom@%all !>

exampleuser@browsegood !> as tom browse
(browse output here)
exampleuser@browsegood !>
""", 'children':{
      '[KEYNAME]':{
        'name':'askeyname', 'callback':command_callbacks.as_keyname, 'priority':True,
      'example': '(command)', 'summary': 'Sets the default identity globally or for an operation.',
      'help_text':'', 'children':{
      }},
  }},


  'help':{
    'name':'help', 'callback':print_help, 'priority':True,
    'cmdgroup':None, 'help_text':"""
A target can be either a host:port:vesselname, %ID, or a group name.

See https://seattle.poly.edu/wiki/RepyTutorial for more info!""",
    'children':{}},
  'show':{
    'name':'show', 'callback':command_callbacks.show,
    'summary': "Displays the shell state (see 'help show')", 'help_text':"""
Displays information regarding the current state of Seattle, depending on
the additional keywords that are passed in.

  (*) No need to update prior, the command contacts the nodes anew

""", 'children':{
      'info':{
        'name':'info', 'callback':command_callbacks.show_info,
        'summary':'Display general information about the vessels','help_text':"""
show info

This command prints general information about vessels in the default group
including the version, nodeID, etc.

Example:
exampleuser@%1 !> show info
192.x.x.178:1224:v3 has no information (try 'update' or 'list')
exampleuser@%1 !> update
exampleuser@%1 !> show info
192.x.x.178:1224:v3 {'nodekey': {'e': 65537L, 'n': 929411623458072017781884599109L}, 'version': '0.1r', 'nodename': '192.x.x.175'}

""", 'children':{}},
      'users':{
        'pattern':'users', 'name':'users', 'callback':command_callbacks.show_users,
        'summary':'Display the user keys for the vessels','help_text':"""
show users

This command lists the set of user keys for vessels in the default group.   
If the key has been loaded into seash as an identity, this name will be used.

Example:
exampleuser@browsegood !> show users
192.x.x.178:1224:v3 has no information (try 'update' or 'list')
192.x.x.2:1224:v12 has no information (try 'update' or 'list')
192.x.x.2:1224:v3 has no information (try 'update' or 'list')
exampleuser@browsegood !> update
exampleuser@browsegood !> show users
192.x.x.178:1224:v3 (no keys)
192.x.x.2:1224:v12 65537 136475...
192.x.x.2:1224:v3 exampleuser

""", 'children':{}},
      'ownerinfo':{
        'name':'ownerinfo', 'callback':command_callbacks.show_ownerinfo,
        'summary':'Display owner information for the vessels','help_text':"""
show ownerinfo

This lists the ownerinfo strings for vessels in the default group.   See
'set ownerinfo' for more details
""", 'children':{}},
      'advertise':{
        'name':'advertise', 'callback':command_callbacks.show_advertise,
        'summary':"Shows whether the node manager will advertise the vessel's keys in the advertise services.", 'help_text':"""
show advertise

This indicates whether the node manager will advertise the vessel's keys in 
the advertise services.   See 'set advertise' for more details.
""", 'children':{}},
      'ip':{
        'name':'ip', 'callback':command_callbacks.show_ip, 'example': '[to file]',
        'summary':'Display the ip addresses of the nodes', 'help_text':"""
show ip 
show ip [to file]

This lists the ip addresses of the vessels in the default group.   These IP
addresses may be optionally written to a file.   

Note that machines behind a NAT, mobile devices, or other systems with 
atypical network connectivity may list a host name instead.

Example:
exampleuser@ !> show targets
browsegood ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%4 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v12']
%3 ['193.x.x.42:1224:v18']
%2 ['192.x.x.2:1224:v3']
exampleuser@ !> on browsegood
exampleuser@browsegood !> show ip
192.x.x.2
193.x.x.42
219.x.x.62

""", 'children':{
          'to':{
            'name':'to', 'callback':None, 'example': '[filename]',
            'summary': 'Outputs the list of ip addresses of the vessels in the default group to [filename]',
            'help_text':'', 'children':{
              '[FILENAME]':{'name':'filename', 'callback':command_callbacks.show_ip_to_file, 'help_text':'', 'children':{}},
          }},
          '>':{
            'name':'>', 'callback':None, 'example': '[filename]',
            'summary': 'Outputs the list of ip addresses of the vessels in the default group to [filename]',
            'help_text':'', 'children':{
              '[FILENAME]':{'name':'filename', 'callback':command_callbacks.show_ip_to_file, 'help_text':'', 'children':{}},
          }},
      }},
      'hostname':{
        'name':'hostname', 'callback':command_callbacks.show_hostname,
        'summary':'Display the hostnames of the nodes','help_text':"""
show hostname

This lists the DNS host names for the vessels in the default group.   If this
information is not available, this will be listed.

Example:
exampleuser@browsegood !> show ip
192.x.x.2
193.x.x.42
219.x.x.62
exampleuser@browsegood !> show hostname
192.x.x.2 is known as Guest-Laptop.home
193.x.x.42 is known as pl2.maskep.aerop.fr
219.x.x.62 has unknown host information

""", 'children':{}},
      'owner':{'name':'owner', 'callback':command_callbacks.show_owner, 'help_text':"""
show owner

Displays the owner key (or identity if known) for the vessels in the default
group.

Example:
exampleuser@ !> show targets
browsegood ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%4 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v12']
%3 ['193.x.x.42:1224:v18']
%2 ['192.x.x.2:1224:v3']
exampleuser@ !> on browsegood
exampleuser@browsegood !> show owner
192.x.x2:1224:v12 exampleuser pubkey
192.x.x.2:1224:v3 65537 127603...
193.x.x.42:1224:v18 65537 163967...
219.x.x.62:1224:v4 65537 952875...

""", 'children':{}},
      'targets':{
        'name':'targets', 'callback':command_callbacks.show_targets,
        'summary':'Display a list of targets','help_text':"""
show targets

Lists the known targets (groups and individual nodes) that commands may be 
run on.

Example:
exampleuser@ !> show targets
%all (empty)
exampleuser@ !> browse
['192.x.x.2:1224', '219.x.x.62:1224', '193.x.x.42:1224']
Added targets: %3(193.x.x.42:1224:v18), %4(219.x.x.62:1224:v4), %1(192.x.x.2:1224:v12), %2(192.x.x.2:1224:v3)
Added group 'browsegood' with 4 targets
yaluen@ !> show targets
browsegood ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%4 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v12']
%3 ['193.x.x.42:1224:v18']
%2 ['192.x.x.2:1224:v3']

""", 'children':{}},
      'groups':{
        'name':'groups', 'callback':command_callbacks.show_groups,
        'summery':'Display a list of groups','help_text':"""
show groups

Lists available groups.

Example:
exampleuser@ !> show groups
%all []
exampleuser@ !> browse
['192.x.x.2:1224', '219.x.x.62:1224', '193.x.x.42:1224']
Added targets: %3(193.x.x.42:1224:v18), %4(219.x.x.62:1224:v4), %1(192.x.x.2:1224:v12), %2(192.x.x.2:1224:v3)
Added group 'browsegood' with 4 targets
exampleuser@ !> show groups
browsegood ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v12', '192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']

""", 'children':{}},
      'identities':{
        'name':'identities', 'callback':command_callbacks.show_identities,
        'summary':'Display the known identities', 'help_text':"""
show identities

Lists the identities loaded into the shell and whether the public or private
keys are loaded.   This does not display the keys themselves (see 'show keys').

Example:
 !> show identities
 !> loadkeys exampleuser
 !> loadkeys guest0
 !> loadkeys guest1
 !> show identities
guest2 PRIV
exampleuser PUB PRIV
guest0 PUB PRIV
guest1 PUB PRIV

""", 'children':{}},
      'keys':{
        'name':'keys', 'callback':command_callbacks.show_keys,
        'summary':'Display the known keys', 'help_text':"""
show keys

List the actual keys loaded by the shell.   To see identity information, see
'show identities'.

Example:
 !> show keys
 !> loadkeys yaluen
 !> loadpub guest0
 !> loadpriv guest1
 !> show keys
exampleuser {'e': 65537L, 'n': 967699203053798948061567293973111925102424779L} {'q': 130841985099129780748709L, 'p': 739593793918579524787167931524344434698161314501292256851220768397231L, 'd': 9466433905223884723074560052831388470409993L}
guest0 {'e': 65537L, 'n': 9148459067481753275566379538357634516166379961L} None
guest1 None {'q': 121028014346935113507847L, 'p': 107361553689073802754887L, 'd': 127298628609806695961451784003754746302524139001L}

""", 'children':{}},
      'log':{
        'name':'log', 'callback':command_callbacks.show_log,
        'example': '[to file]', 'summary':'Display the log from the vessel (*)', 'help_text':"""
Lists the log of operations from the vessel.   This log is populated by print
statements and exceptions from the program running in the vessel.
""", 'children':{
          'to':{
            'name':'to', 'callback':None, 'example': '[filename]',
            'summary': 'Writes the log to a file.', 'help_text':'', 'children':{
              '[FILENAME]':{'name':'filename', 'callback':command_callbacks.show_log_to_file, 'help_text':'', 'children':{}},
          }},
      }},
      'files':{
        'name':'files', 'callback':command_callbacks.show_files,
        'summary':'Display a list of files in the vessel (*)', 'help_text':"""
show files

Lists the names of the files loaded into vessels in the default groups.   
This is similar to dir or ls.

Example:
exampleuser@browsegood !> show files
Files on '192.x.x.2:1224:v3': ''
Files on '193.x.x.42:1224:v18': ''
Files on '219.x.x.62:1224:v4': ''
exampleuser@browsegood !> upload example.1.1.r2py
exampleuser@browsegood !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.r2py'
Files on '193.x.x.42:1224:v18': 'example.1.1.r2py'
Files on '219.x.x.62:1224:v4': 'example.1.1.r2py'

""", 'children':{}},
      'resources':{
        'name':'resources', 'callback':command_callbacks.show_resources,
        'summary':'Display the resources / restrictions for the vessel (*)', 'help_text':"""
show resources

Lists the resources allotted to vessels in the default group.
""", 'children':{}},
      'offcut':{
        'name':'offcut', 'callback':command_callbacks.show_offcut,
        'summary':'Display the offcut resource for the node (*)', 'help_text':"""
show offcut

This lists the amount of resources that will be lost by splitting a vessel or
gained by joining two vessels.   This is shown on a per-node basis amongst
all vessels in the default group
""", 'children':{}},
      'timeout':{
        'name':'timeout', 'callback':command_callbacks.show_timeout,
        'summary':'Display the timeout for nodes', 'help_text':"""
show timeout

This shows the amount of time the shell will wait for a command to timeout.   
Note that commands like 'run' and 'upload' will use both this value and the
uploadrate setting

Example:
 !> show timeout
10

""", 'children':{}},
      'uploadrate':{
        'name':'uploadrate', 'callback':command_callbacks.show_uploadrate,
        'summary':'Display the upload rate which seash uses to estimate the required time for a file upload', 'help_text':"""
show uploadrate

This lists the minimum rate at which the shell should allow uploads to occur.
Uploads to vessels that go slower than this will be aborted.   Note that this
is used in combination with the timeout setting.

Example:
 !> show uploadrate
102400

""", 'children':{}},
  }},


  'run':{
    'name':'run', 'callback':None, 'example':'file [args ...]',
    'summary':'Upload a file and start executing it', 'help_text':"""
Uploads a program to a vessel and starts it running.   (This command is
actually just a short-cut for the 'upload' and 'start' commands).   The
arguments listed will be passed to the command when it is started.

This command will make an educated guess as to what platform your
program is written for (i.e. repyV1 or repyV2).  You can override this
by using 'runv1' or 'runv2', respectively.

Example:
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':

Log from '193.x.x.42:1224:v18':

Log from '219.x.x.62:1224:v4':

Log from '192.x.x.2:1224:v12':

exampleuser@browsegood !> run example.1.1.r2py
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':
Hello World

Log from '193.x.x.42:1224:v18':
Hello World

Log from '219.x.x.62:1224:v4':
Hello World

Log from '192.x.x.2:1224:v12':
Hello World

""", 'children':{
      '[FILENAME]':{
        'name':'filename', 'callback':command_callbacks.run_localfn, 'example':'[arg1, arg2, ...]',
        'summary': 'Uploads the file to the vessels and starts running them, passing arguments if specified.',
        'help_text':'','children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.run_localfn_arg, 'help_text':'', 'children':{}},
      }},
  }},

  'runv1':{
    'name':'run', 'callback':None, 'example':'file [args ...]',
    'summary':'Upload a file and start executing it as repyV1', 'help_text':"""
Uploads a program to a vessel and starts it running.   (This command is
actually just a short-cut for the 'upload' and 'startv1' commands).
The arguments listed will be passed to the command when it is started.

Example:
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':

Log from '193.x.x.42:1224:v18':

Log from '219.x.x.62:1224:v4':

Log from '192.x.x.2:1224:v12':

exampleuser@browsegood !> run example.1.1.r2py
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':
Hello World

Log from '193.x.x.42:1224:v18':
Hello World

Log from '219.x.x.62:1224:v4':
Hello World

Log from '192.x.x.2:1224:v12':
Hello World

""", 'children':{
      '[FILENAME]':{
        'name':'filename', 'callback':command_callbacks.run_localfn, 'example':'[arg1, arg2, ...]',
        'summary': 'Uploads the file to the vessels and starts running them, passing arguments if specified.',
        'help_text':'','children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.run_localfn_arg, 'help_text':'', 'children':{}},
      }},
  }},


  'runv2':{
    'name':'run', 'callback':None, 'example':'file [args ...]',
    'summary':'Upload a file and start executing it as repyV2', 'help_text':"""
Uploads a program to a vessel and starts it running.   (This command is
actually just a short-cut for the 'upload' and 'startv2' commands).
The arguments listed will be passed to the command when it is started.

Example:
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':

Log from '193.x.x.42:1224:v18':

Log from '219.x.x.62:1224:v4':

Log from '192.x.x.2:1224:v12':

exampleuser@browsegood !> run example.1.1.r2py
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':
Hello World

Log from '193.x.x.42:1224:v18':
Hello World

Log from '219.x.x.62:1224:v4':
Hello World

Log from '192.x.x.2:1224:v12':
Hello World

""", 'children':{
      '[FILENAME]':{
        'name':'filename', 'callback':command_callbacks.run_localfn, 'example':'[arg1, arg2, ...]',
        'summary': 'Uploads the file to the vessels and starts running them, passing arguments if specified.',
        'help_text':'','children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.run_localfn_arg, 'help_text':'', 'children':{}},
      }},
  }},

  'runv1':{
    'name':'run', 'callback':None, 'example':'file [args ...]',
    'summary':'Upload a file and start executing it as repyV1', 'help_text':"""
Uploads a program to a vessel and starts it running.   (This command is
actually just a short-cut for the 'upload' and 'startv1' commands).
The arguments listed will be passed to the command when it is started.

Example:
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':

Log from '193.x.x.42:1224:v18':

Log from '219.x.x.62:1224:v4':

Log from '192.x.x.2:1224:v12':

exampleuser@browsegood !> run example.1.1.r2py
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':
Hello World

Log from '193.x.x.42:1224:v18':
Hello World

Log from '219.x.x.62:1224:v4':
Hello World

Log from '192.x.x.2:1224:v12':
Hello World

""", 'children':{
      '[FILENAME]':{
        'name':'filename', 'callback':command_callbacks.run_localfn, 'example':'[arg1, arg2, ...]',
        'summary': 'Uploads the file to the vessels and starts running them, passing arguments if specified.',
        'help_text':'','children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.run_localfn_arg, 'help_text':'', 'children':{}},
      }},
  }},


  'runv2':{
    'name':'run', 'callback':None, 'example':'file [args ...]',
    'summary':'Upload a file and start executing it as repyV2', 'help_text':"""
Uploads a program to a vessel and starts it running.   (This command is
actually just a short-cut for the 'upload' and 'startv2' commands).
The arguments listed will be passed to the command when it is started.

Example:
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':

Log from '193.x.x.42:1224:v18':

Log from '219.x.x.62:1224:v4':

Log from '192.x.x.2:1224:v12':

exampleuser@browsegood !> run example.1.1.r2py
exampleuser@browsegood !> show log
Log from '192.x.x.2:1224:v3':
Hello World

Log from '193.x.x.42:1224:v18':
Hello World

Log from '219.x.x.62:1224:v4':
Hello World

Log from '192.x.x.2:1224:v12':
Hello World

""", 'children':{
      '[FILENAME]':{
        'name':'filename', 'callback':command_callbacks.run_localfn, 'example':'[arg1, arg2, ...]',
        'summary': 'Uploads the file to the vessels and starts running them, passing arguments if specified.',
        'help_text':'','children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.run_localfn_arg, 'help_text':'', 'children':{}},
      }},
  }},


  'add':{
    'name':'add', 'callback':None, 'example': '[target] [to group]',
    'summary':'Adds a target (a vessel name or group) to a group', 'help_text':"""
add target [to group]
add to group

Adds a target (a vessel name or group) a group.   If the group does not exist,
it is created.   This can be used to control which vessels are manipulated by 
different commands.   The short form 'add target' adds the target to the 
default group.   The short form 'add to group' adds the default group to
the target.

If the target is already in the group, an error message will be printed.

Example:
exampleuser@%1 !> on new_group
Invalid command input: Target does not exist
exampleuser@%1 !> add to new_group
exampleuser@%1 !> add %2 to new_group
exampleuser@%1 !> on new_group
exampleuser@new_group !> list
  ID Own                      Name     Status              Owner Information
  %1  *        192.x.x.178:1224:v3      Fresh                               
  %2  *         192.x.x.2:1224:v12      Fresh    

""", 'children':{
      '[TARGET]':{
        'name':'target', 'callback':command_callbacks.add_target,
        'example': 'to group', 'summary': 'Adds a target to a group.', 'help_text':'', 'children':{
          'to':{'name':'to', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.add_target_to_group, 'help_text':'', 'children':{}},
          }},
      }},
      'to':{
        'name':'to', 'callback':None, 'example': 'group',
        'summary':'Adds the default target to a group.', 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.add_to_group, 'help_text':'', 'children':{}},
      }},
  }},


  'move':{
    'name':'move', 'callback':None, 'example': 'target to group',
    'summary': 'Add target to group, remove target from default', 'cmdgroup': 'extended', 'help_text':"""
This is essentially a shortcut for removing the target from the default group
and adding it to group.   See 'add' and 'remove' for more information.
""", 'children':{
      '[TARGET]':{
        'name':'target', 'callback':None, 'example': 'to group',
        'summary': 'Moves the target to the group', 'help_text':'', 'children':{
          'to':{'name':'to', 'callback':None, 'help_text':'', 'children':{
              '[GROUP]':{'name':'group', 'callback':command_callbacks.move_target_to_group, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'remove':{
    'name':'remove', 'callback':None, 'example':'[target] [from group]',
    'summary':'Removes a target from a group', 'help_text':"""
remove [target] from group

This command removes a target (vesselname or group) from a group.   This means
that future group operations will not include the listed vesselname or group.
The short form 'remove target' removes the target from the default group.
The short form 'remove from group' removes the default group from group.

If the target is not in the group, an error message will be printed.

Example:
exampleuser@new_group !> list
  ID Own                      Name     Status              Owner Information
  %1  *        192.x.x.178:1224:v3      Fresh                               
  %2  *         192.x.x.2:1224:v12      Fresh    
  %3             192.x.x.2:1224:v3      Fresh      
exampleuser@new_group !> on %1
exampleuser@%1 !> remove from new_group
exampleuser@%1 !> remove %2 from new_group
exampleuser@%1 !> on new_group
exampleuser@new_group !> list
  ID Own                      Name     Status              Owner Information
  %3             192.x.x.2:1224:v3      Fresh   

""", 'children':{
      '[TARGET]':{
        'name':'target', 'callback':command_callbacks.remove_target, 'example':'from group',
        'summary': 'Removes the target from the default group', 'help_text':'', 'children':{
          'from':{'name':'from', 'callback':None, 'help_text':'', 'children':{
            '[GROUP]':{
              'name':'group', 'callback':command_callbacks.remove_target_from_group,
              'summary': 'Removes the target from the group', 'help_text':'',
              'children':{}},
          }},
      }},
      'from':{
        'name':'from', 'callback':None, 'example': 'group',
        'summary': 'Removes the default group from group', 'help_text':'', 'children':{
          '[GROUP]':{'name':'group', 'callback':command_callbacks.remove_from_group, 'help_text':'', 'children':{}},
      }},
  }},


  'set':{
    'name':'set', 'callback':command_callbacks.set,
    'summary': "Changes the shell or vessels (see 'help set')", 'help_text':"""
Changes the shell or vessels.
""", 'children':{
      'users':{
        'name':'users', 'callback':None, 'example':'[identity ...]',
        'summary':"Change a vessel's users", 'help_text':"""
set users [identity1, identity2, ...]

Sets the user keys for vessels in the default group.   The current identity
must own the vessels.

Example:
exampleuser@%1 !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
exampleuser@%1 !> show users
192.x.x.2:1224:v12 65537 136475...
exampleuser@%1 !> set users guest0 guest1 guest2
exampleuser@%1 !> update
exampleuser@%1 !> show users
192.x.x.2:1224:v12 guest0 guest1 guest2
exampleuser@%1 !> on %2
exampleuser@%2 !> show owner
192.x.x.2:1224:v3 65537 127603...
exampleuser@%2 !> set users guest0 guest1
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_users_arg, 'help_text':'', 'children':{}},
      }},
      'ownerinfo':{
        'name':'ownerinfo', 'callback':None, 'example': '[ data ... ]',
        'summary': 'Change owner information for the vessels', 'help_text':"""
set ownerinfo 'string'

This command sets the owner information for each vessel in the default group.
The default identity must own the vessels.

Example:
exampleuser@browsegood !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
192.x.x.2:1224:v3 65537 127603...
exampleuser@browsegood !> show ownerinfo
192.x.x.2:1224:v12 ''
192.x.x.2:1224:v3 ''
exampleuser@browsegood !> set ownerinfo Example owner info
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3
Added group 'ownerinfogood' with 1 targets and 'ownerinfofail' with 1 targets
exampleuser@browsegood !> update
exampleuser@browsegood !> show ownerinfo
192.x.x.2:1224:v12 'Example owner info'
192.x.x.2:1224:v3 ''

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_ownerinfo_arg, 'help_text':'', 'children':{}},
      }},
      'advertise':{
        'name':'advertise', 'callback':None,
        'summary':'Change advertisement information about the vessels','help_text':"""
set advertise [on/off]

This setting is changable only by the vessel owner and indicates whether or
not the node's IP / port should be advertised under the owner and user keys.
The default value is on.   With this turned off, the 'browse' command will
be unable to discover the vessel.

exampleuser@%1 !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
exampleuser@%1 !> show advertise
192.x.x.2:1224:v12 on
exampleuser@%1 !> set advertise off
exampleuser@%1 !> update
exampleuser@%1 !> show advertise
192.x.x.2:1224:v12 off
exampleuser@%1 !> on %2
exampleuser@%2 !> show owner
192.x.x.2:1224:v3 65537 127603...
exampleuser@%2 !> show advertise
192.x.x.2:1224:v3 on
exampleuser@%2 !> set advertise off
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_advertise_arg, 'help_text':'', 'children':{}},
      }},
      'owner':{
        'name':'owner', 'callback':None, 'example': 'identity',
        'summary': "Changes a vessel's owner.", 'help_text':"""
set owner identity

This changes the owner key for all vessels in the default group to the
identity specified.   This command may only be issued by the vessels' current
owner.

Example:
exampleuser@%1 !> show identities
exampleuser PUB PRIV
guest0 PUB PRIV
guest1 PUB PRIV
exampleuser@%1 !> show owner
192.x.x.2:1224:v12 exampleuser pubkey
exampleuser@%1 !> set owner guest0
exampleuser@%1 !> update
exampleuser@%1 !> show owner
192.x.x.2:1224:v12 guest0 pubkey
exampleuser@%1 !> on %2
exampleuser@%2 !> show owner
192.x.x.2:1224:v3 65537 127603...
exampleuser@%2 !> set owner exampleuser
Failure 'Node Manager error 'Insufficient Permissions'' on  192.x.x.2:1224:v3

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_owner_arg, 'help_text':'', 'children':{}},
      }},
      'timeout':{
        'name':'timeout', 'callback':None, 'example': 'count',
        'summary': 'Sets the time that seash is willing to wait on a node',
        'help_text':"""
set timeout timeoutval

This sets the timeout for network related commands.   Most commands will then
be aborted on nodes if they are not completed withing the timeoutval number of
seconds.   Note that the upload and run commands also use the uploadrate 
setting to determine their timeout.

Example:
exampleuser@%1 !> set timeout 1
exampleuser@%1 !> show timeout
1
exampleuser@%1 !> start example.1.1.r2py
Failure 'signedcommunicate failed on session_recvmessage with error 'recv() timed out!'' uploading to 193.x.x.42:1224:v18
exampleuser@%1 !> set timeout 10
exampleuser@%1 !> start example.1.1.r2py
exampleuser@%1 !> show log
Log from '193.x.x.42:1224:v18':
Hello World

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_timeout_arg, 'help_text':'', 'children':{}},
      }},
      'uploadrate':{
        'name':'uploadrate', 'callback':None, 'example': 'speed',
        'summary': 'Sets the upload rate which seash will use to estimate the time needed for a file to be uploaded to a vessel. The estimated time would be set as the temporary timeout count during actual process. Speed should be in bytes/sec.',
        'help_text':"""
set uploadrate rate_in_bps

This value is used along with the timeout value to determine when to declare an
upload or run command as failed.   The wait time is computed as:
   timeout + filesize / rate_in_bps

Thus if the timeout is 10 seconds and rate_in_bps is 102400 (100 KB / s), a 1MB 
will attempt to upload for 20 seconds.

Example:
exampleuser@%1 !> set uploadrate 99999999999999
exampleuser@%1 !> set timeout 1
exampleuser@%1 !> upload example.1.1.r2py
Failure 'signedcommunicate failed on session_recvmessage with error 'recv() timed out!'' uploading to 193.x.x.42:1224:v18
exampleuser@%1 !> set uploadrate 102400
exampleuser@%1 !> upload example.1.1.r2py
exampleuser@%1 !> 

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_uploadrate_arg, 'help_text':'', 'children':{}},
      }},
      'autosave':{
        'name':'autosave', 'callback':None, 'example': '[ on | off ]',
        'summary': "Sets whether to save the state after every command. Set to 'off' by default. The state is saved to a file called 'autosave_keyname', where keyname is the name of the current key you're using.",
        'help_text':"""
set autosave [on/off]

When turned on, the shell settings such as keys, targets, timeout value, etc.
will all be persisted to disk after every operation.   These are saved in a
file called 'autosave_(user's keyname)', which is encrypted with the default identity.   The user
can then restore the shell's state by typing 'loadstate identity'.

Example:
exampleuser@%1 !> set autosave on
exampleuser@%1 !> exit
(restart seash.py)
 !> loadkeys exampleuser
 !> as exampleuser
exampleuser@ !> loadstate autosave_exampleuser
exampleuser@%1 !>

""", 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_autosave_arg, 'help_text':'', 'children':{}},
      }},
      'showparse': {
        'name':'showparse', 'callback': None, 'example': '[ on | off ]', 
        'summary': 'Toggle display of parsed command line input', 'help_text':"""
set showparse [on/off]

When turned on, when any modules modify the command line input, the resulting
input will be printed to the screen.

Example:
exampleuser@%1 !> set showparse on
exampleuser@%1 !> set username exampleuser2
exampleuser@%1 !> as $username
as exampleuser2
exampleuser2@%1 !> set showparse off
exampleuser2@%1 !> as $username
exampleuser2@%1 !>

""", 'children': {
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.set_showparse_args, 'help_text':'', 'children':{}},
      }},
  }},


  'browse':{
    'name':'browse', 'callback':command_callbacks.browse,
    'summary': 'Find vessels I can control', 'help_text':"""
browse [advertisetype]

This command will use the default identity to search for vessels that can
be controlled.   Any vessel with the advertise flag set will be advertised
in at least one advertise service.   browse will look into these services
and add any vessels it can contact.

Setting advertisetype will restrict the advertise lookup to only use that 
service.   Some permitted values for advertisetype are central, DHT, and DOR.

Example:
exampleuser@ !> show targets
%all (empty)
exampleuser@ !> browse
['192.x.x.2:1224', '193.x.x.42:1224', '219.x.x.62:1224']
Added targets: %2(193.x.x.42:1224:v18), %3(219.x.x.62:1224:v4), %1(192.x.x.2:1224:v3)
Added group 'browsegood' with 3 targets
exampleuser@ !> show targets
browsegood ['192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%3 ['219.x.x.62:1224:v4']
%all ['192.x.x.2:1224:v3', '193.x.x.42:1224:v18', '219.x.x.62:1224:v4']
%1 ['192.x.x.2:1224:v3']
%2 ['193.x.x.42:1224:v18']

""", 'children':{
      '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.browse_arg, 'help_text':'', 'children':{}},
  }},


  'genkeys':{
    'name':'genkeys', 'callback':None, 'example':'fn [len] [as identity]',
    'summary':'Creates new pub / priv keys (default len=1024)', 'cmdgroup': 'extended', 'help_text':"""
genkeys keyprefix [as identity]

Generates a new set of keys, writing them to files keyprefix.publickey and
keyprefix.privatekey.   It also adds the identity under the name given.  If
identity is not specified, keyprefix is used.

Example:
 !> genkeys userA as userB
Created identity 'userB'
 !> show identities
userB PUB PRIV
 !> loadkeys userA
 !> show identities
userB PUB PRIV
userA PUB PRIV

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.genkeys_filename, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.genkeys_filename_len, 'help_text':'', 'children':{
              'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
                  '[ARGUMENT]':{'name':'keyname', 'callback':command_callbacks.genkeys_filename_len_as_identity, 'help_text':'', 'children':{}},
              }},
          }},
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'keyname', 'callback':command_callbacks.genkeys_filename_as_identity, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'loadkeys':{
    'name':'loadkeys', 'callback':None, 'example': 'fn [as identity]',
    'summary':'Loads filename.publickey and filename.privatekey', 'help_text':"""
loadkeys keyprefix [as identity]

Loads a public key named keyprefix.publickey and a private key named
keyprefix.privatekey.   This is a shortcut for the 'loadpub' and 'loadpriv'
operations.   If identity is specified, the shell refers to the keys using
this.   If not, keyprefix is the identity.

Example:
 !> loadkeys exampleuser
 !> show identities
exampleuser PUB PRIV
 !> as exampleuser
exampleuser@ !>

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadkeys_keyname, 'help_text':'', 'children':{
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.loadkeys_keyname_as, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'loadpub':{
    'name':'loadpub', 'callback':None, 'example':'fn [as identity]',
    'summary':'Loads filename.publickey', 'cmdgroup': 'extended', 'help_text':"""
loadpub pubkeyfile [as identity]

Loads a public key named keyprefix.publickey.  If identity is specified, the 
shell refers to the keys using this.   If not, keyprefix is the identity.

Example:
 !> loadpub exampleuser
 !> show identities
exampleuser PUB

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadpub_filename, 'help_text':'', 'children':{
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.loadpub_filename_as, 'help_text':'', 'children':{}},
          }},
      }},
  }},


  'loadpriv':{
    'name':'loadpriv', 'callback':None, 'example':'fn [as identity]',
    'summary':'Loads filename.privatekey', 'cmdgroup': 'extended',
    'help_text':"""
loadpriv privkeyfile [as identity]

Loads a private key named keyprefix.privatekey.  If identity is specified, the 
shell refers to the keys using this.   If not, keyprefix is the identity.

Example:
 !> loadpriv exampleuser
 !> show identities
exampleuser PRIV

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadpriv_filename, 'help_text':'', 'children':{
          'as':{'name':'as', 'callback':None, 'help_text':'', 'children':{
              '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.loadpriv_filename_as, 'help_text':'', 'children':{}},
          }},
      }},
  }},

  
  'list':{
    'name':'list', 'callback':command_callbacks.list,
    'summary':'Update and display information about the vessels', 'help_text':"""
list

Display status information about a set of vessels.   This indicates whether
the vessels are running programs, if the default identity is the owner or
just a user, along with other useful information.

Example:
exampleuser@browsegood !> list
  ID Own                      Name     Status              Owner Information
  %1  *        192.x.x.178:1224:v3      Fresh                               
  %2  *         192.x.x.2:1224:v12      Fresh                               
  %3             192.x.x.2:1224:v3      Fresh  

""", 'children':{}},


  'upload':{
    'name':'upload', 'callback':None, 'example':'localfn (remotefn)',
    'summary': 'Upload a file', 'help_text':"""
upload srcfilename [destfilename]

Uploads a file into all vessels in the default group.   The file name that is
created in those vessels is destfilename (or srcfilename by default).

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': ''
exampleuser@%1 !> upload example.1.1.r2py
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.r2py'

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.upload_filename, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.upload_filename_remotefn, 'help_text':'', 'children':{}}
      }},
  }},


  'download':{
    'name':'download', 'callback':None, 'example':'remotefn (localfn)',
    'summary': 'Download a file (to multiple local files)', 'help_text':"""
download srcfilename [destfilename]

Retrieves a copy of srcfilename from every vessel in the default group.   The
file is written as the destfilename.vesselname (with ':' replaced with '_').
If the destfilename is not specified, srcfilename is used instead.

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.r2py'
exampleuser@%1 !> download example.1.1.r2py
Wrote files: example.1.1.r2py.192.x.x.2_1224_v3 
yaluen@%1 !> download example.1.1.r2py test_download
Wrote files: test_download.192.x.x.2_1224_v3 

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.download_filename, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.download_filename_localfn, 'help_text':'', 'children':{}}
      }},
  }},


  'delete':{
    'name':'delete', 'callback':None, 'example': 'remotefn',
    'summary': 'Delete a file.', 'help_text':"""
delete filename

Erases filename from every vessel in the default group.

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.r2py'
exampleuser@%1 !> delete example.1.1.r2py
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': ''

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.delete_remotefn, 'help_text':'', 'children':{}},
  }},

  'cat':{
    'name':'cat', 'callback':None, 'example':'remotefn',
    'summary':'Display the contents of a remote file', 'help_text':"""
cat filename

Displays the content of filename from every vessel in the default group.

Example:
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.r2py'
exampleuser@%1 !> cat example.1.1.r2py

File 'example.1.1.r2py' on '192.168.1.2:1224:v3': 
if callfunc == 'initialize':
  print "Hello World"

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.cat_filename, 'help_text':'', 'children':{}},
  }},


  'reset':{
    'name':'reset', 'callback':command_callbacks.reset,
    'summary':'Reset the vessel (clear files / log and stop)', 'help_text':"""
reset

Clears the log, stops any programs, and deletes all files from every vessel
in the default group.

Example:
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1           192.x.x.2:1224:v3 Terminated                               
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': 'example.1.1.r2py'
exampleuser@%1 !> reset
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':

exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1           192.x.x.2:1224:v3      Fresh                               
exampleuser@%1 !> show files
Files on '192.x.x.2:1224:v3': '' 

""", 'children':{}},


  'start':{
    'name':'start', 'callback':None, 'example':'file [args ...]',
    'summary':"Start an experiment (doesn't upload)", 'cmdgroup': 'extended', 'help_text':"""
start programname [arg1 arg2 ...]

Begins executing a file in the vessel named programname with the given 
arguments.   This program must first be uploaded to the vessel (the 'run'
command does this for the user).

This command will make an educated guess as to what platform your
program is written for (i.e. repyV1 or repyV2).  You can override this
by using 'startv1' or 'startv2', respectively.

Example:
exampleuser@%1 !> upload example.1.1.r2py
exampleuser@%1 !> start example.1.1.r2py
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.start_remotefn, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.start_remotefn_arg, 'help_text':'', 'children':{}},
      }},
  }},

  'startv1':{
    'name':'start', 'callback':None, 'example':'file [args ...]',
    'summary':"Start an experiment (doesn't upload) in repyV1", 'cmdgroup': 'extended', 'help_text':"""
start programname [arg1 arg2 ...]

Begins executing a file in the vessel named programname with the given
arguments in repyv1.   This program must first be uploaded to the vessel
(the 'run' command does this for the user).

Example:
exampleuser@%1 !> upload example.1.1.r2py
exampleuser@%1 !> start example.1.1.r2py
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.start_remotefn, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.start_remotefn_arg, 'help_text':'', 'children':{}},
      }},
  }},

  'startv2':{
    'name':'start', 'callback':None, 'example':'file [args ...]',
    'summary':"Start an experiment (doesn't upload) in repyV2", 'cmdgroup': 'extended', 'help_text':"""
start programname [arg1 arg2 ...]

Begins executing a file in the vessel named programname with the given
arguments in repyv2.   This program must first be uploaded to the vessel
(the 'run' command does this for the user).

Example:
exampleuser@%1 !> upload example.1.1.r2py
exampleuser@%1 !> start example.1.1.r2py
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.start_remotefn, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.start_remotefn_arg, 'help_text':'', 'children':{}},
      }},
  }},

  'startv1':{
    'name':'start', 'callback':None, 'example':'file [args ...]',
    'summary':"Start an experiment (doesn't upload) in repyV1", 'cmdgroup': 'extended', 'help_text':"""
start programname [arg1 arg2 ...]

Begins executing a file in the vessel named programname with the given
arguments in repyv1.   This program must first be uploaded to the vessel
(the 'run' command does this for the user).

Example:
exampleuser@%1 !> upload example.1.1.r2py
exampleuser@%1 !> start example.1.1.r2py
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.start_remotefn, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.start_remotefn_arg, 'help_text':'', 'children':{}},
      }},
  }},

  'startv2':{
    'name':'start', 'callback':None, 'example':'file [args ...]',
    'summary':"Start an experiment (doesn't upload) in repyV2", 'cmdgroup': 'extended', 'help_text':"""
start programname [arg1 arg2 ...]

Begins executing a file in the vessel named programname with the given
arguments in repyv2.   This program must first be uploaded to the vessel
(the 'run' command does this for the user).

Example:
exampleuser@%1 !> upload example.1.1.r2py
exampleuser@%1 !> start example.1.1.r2py
exampleuser@%1 !> show log
Log from '192.x.x.2:1224:v3':
Hello World

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.start_remotefn, 'help_text':'', 'children':{
          '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.start_remotefn_arg, 'help_text':'', 'children':{}},
      }},
  }},


  'stop':{
    'name':'stop', 'callback':command_callbacks.stop,
    'summary':'Stop an experiment but leave the log / files', 'help_text':"""
stop

Stops executing the running program in every vessel in the default group.   
The program will halt as though it were killed / interrupted.   The status
for these vessels will become 'Stopped'.

Example:
exampleuser@%1 !> run endless_loop.r2py 
exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1             192.x.x.2:1224:v3    Started                               
exampleuser@%1 !> stop
exampleuser@%1 !> list
  ID Own                      Name     Status              Owner Information
  %1             192.x.x.2:1224:v3    Stopped                                

""", 'children':{}},


  'split':{
    'name':'split', 'callback':None, 'example':'resourcefn',
    'summary':'Split another vessel off (requires owner)', 'cmdgroup': 'extended', 'help_text':"""
split resourcefile

Divides the vessels in the default group into two new vessels.   The first
vessel will have the size specified in the resource file.   The second will
have the remaining size, minus the size of the offcut resources.   The new
vessels will be known to the shell. 

You must be the owner of the vessel to use the split command.

Example:
exampleuser@browsegood !> show targets
browsegood (empty)
joingood ['192.x.x.192:1224:v3', '192.x.x.192:1224:v4']
joinfail (empty)
%all ['192.x.x.192:1224:v11']
%3 ['192.x.x.192:1224:v11']
exampleuser@browsegood !> on %3
exampleuser@%3 !> split resources.offcut
192.x.x.192:1224:v11 -> (192.x.x.192:1224:v12, 192.x.x.192:1224:v13)
Added group 'split1' with 1 targets and 'split2' with 1 targets
exampleuser@%3 !> show targets
split2 ['192.x.x.192:1224:v13']
split1 ['192.x.x.192:1224:v12']
browsegood (empty)
joingood ['192.x.x.192:1224:v3', '192.x.x.192:1224:v4']
joinfail (empty)
%5 ['192.x.x.192:1224:v13']
%4 ['192.x.x.192:1224:v12']
%all ['192.x.x.192:1224:v12', '192.x.x.192:1224:v13']

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.split_resourcefn, 'help_text':'', 'children':{}},
  }},


  'join':{
    'name':'join', 'callback':command_callbacks.join,
    'summary':'Join vessels on the same node (requires owner)', 'cmdgroup': 'extended', 'help_text':"""
join

Joins any vessels in the default group that are on the same node.   The 
resulting vessel will have a size equal to the two other vessels plus the
offcut resource amount.  The new vessels will be known to the shell. 

You must be the owner of the vessels to join them.

Example:
exampleuser@browsegood !> join
Traceback (most recent call last):
  File "seash.py", line 222, in command_loop
  File "/home/user/seattle_test/seash_dictionary.py", line 1458, in command_dispatch
  File "/home/user/seattle_test/command_callbacks.py", line 2485, in join
KeyError: 'ownerkey'
exampleuser@browsegood !> update
exampleuser@browsegood !> show owner
192.x.x.192:1224:v3 guest0 pubkey
192.x.x.192:1224:v4 guest0 pubkey
exampleuser@browsegood !> join
192.x.x.192:1224:v11 <- (192.x.x.192:1224:v3, 192.x.x.192:1224:v4)
Added group 'joingood' with 2 targets
exampleuser@browsegood !> show targets
browsegood (empty)
joingood ['192.x.x.192:1224:v3', '192.x.x.192:1224:v4']
joinfail (empty)
%all ['192.x.x.192:1224:v11']
%3 ['192.x.x.192:1224:v11']

""", 'children':{}},


  'exit':{
    'name':'exit', 'callback':command_callbacks.exit,
    'summary':'Exits the shell', 'help_text':"""
exit

Exits seash.
""", 'children':{}},


  'loadstate':{
    'name':'loadstate', 'callback':None, 'example':'fn',
    'summary':'Load encrypted shell state from a file with the keyname', 'cmdgroup': 'extended',
    'help_text':"""
loadstate filename

Loads state information from filename using the default identity to decrypt
the file.   This will restore all identities, keys, groups, etc. from a 
previous seash run.  See also 'set autosave on/off.'

Example:
exampleuser@%1 !> savestate testing_state
exampleuser@%1 !> exit
(restart seash.py)
 !> loadkeys exampleuser
 !> as exampleuser
exampleuser@ !> loadstate testing_state
exampleuser@%1 !>

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.loadstate_filename, 'help_text':'', 'children':{}},
  }},


  'savestate':{
    'name':'savestate', 'callback':None, 'example':'fn',
    'summary':"Save the shell's state information to a file with the keyname", 'cmdgroup': 'extended',
    'help_text':"""
savestate filename

Saves state information into a filename, encrypting the data with the default 
identity's private key.  This can be later used to restore the shell's 
settings, groups, and other information.   See also 'set autosave on/off.'

Example:
exampleuser@%1 !> savestate testing_state
exampleuser@%1 !> exit
(restart seash.py)
 !> loadkeys exampleuser
 !> as exampleuser
exampleuser@ !> loadstate testing_state
exampleuser@%1 !>

""", 'children':{
      '[FILENAME]':{'name':'filename', 'callback':command_callbacks.savestate_filename, 'help_text':'', 'children':{}},
  }},


  'update':{
    'name':'update', 'callback':command_callbacks.update,
    'summary': 'Update information about the vessels', 'cmdgroup': 'extended',
  'help_text':"""
update

Reacquire cached state from the vessels.   This state is used for many of the
'show' commands to prevent every operation from needing to contact all vessels.

Example:
exampleuser@%1 !> show info
192.x.x.2:1224:v3 has no information (try 'update' or 'list')
exampleuser@%1 !> update
exampleuser@%1 !> show info
192.x.x.2:1224:v3 {'nodekey': {'e': 65537L, 'n': 924563171010915569497668794725930165347860823L}, 'version': '0.1t', 'nodename': '192.x.x.2'}

""", 'children':{}},


  'contact':{
    'name':'contact', 'callback':None, 'example':'host:port[:vessel]',
    'summary': 'Communicate with a node explicitly', 'cmdgroup': 'extended',
    'help_text':"""
contact IP:port[:vesselname]

Add the specified vessel to the shell.   This bypasses advertise lookups and
directly contacts the node manager.   If the vesselname argument is omitted,
all vessels that can be controlled by the default identity are added.

Example:
exampleuser@ !> contact 192.x.x.2:1224
Added targets: %1(192.x.x.2:1224:v3)

""", 'children':{
      '[ARGUMENT]':{'name':'args', 'callback':command_callbacks.contact, 'help_text':'', 'children':{}},
  }},
}


# A dictionary to be built to keep track of the different variations of commands users will input
commandvariationdict = {
  'users':['user'],
  'hostname':['hostnames'],
  'location':['locations'],
  'coordinates':['coordinate'],
  'owner':['owners'],
  'timeout':['timeouts'],
  'targets':['target'],
  'uploadrate':['uploadrates'],
  'identities':['identity'],
  'ip':['ips'],
  'keys':['key'],
  'files':['file'],
  'resources':['resource'],
  'offcut':['offcuts'],
  'genkeys':['genkey'],
  'loadkeys':['loadkey'],
  'exit':['quit']
}


##### All methods that adds to the seash command dictionary #####


# Creates a deep copy of the seash dictionary while avoiding any of the 
# commands in the passed list.
# Only works in the first level of the dictionary. Will not search for the 
# existence of the avoided command in deeper levels of the dictionary.
def _deep_copy_main_dict(avoided_cmds_list):

  command_dict_copy = seashcommanddict.copy()

  # For every command pattern found in the passed list,
  # the function will delete it from
  for cmd in avoided_cmds_list:

    if cmd in command_dict_copy:

      del command_dict_copy[cmd]
  

  return command_dict_copy




# Returns a copy of a command's dictionary with an empty dictionary for its children
def _shallow_copy(cmd_dict):
  cmd_dict_copy = cmd_dict.copy()
  cmd_dict_copy['children'] = {}
  return cmd_dict_copy





# Returns the seash command dictionary after making any necessary additions to it

def return_command_dictionary():
  
  # Sets the entire seash command dictionary as 'on target' children except itself
  seashcommanddict['on']['children']['[TARGET]']['children'] = _deep_copy_main_dict(['on'])
  
  # Sets the entire seash command dictionary as 'as keyname' children except itself
  seashcommanddict['as']['children']['[KEYNAME]']['children'] = _deep_copy_main_dict(['as'])

  # Preserve the old children
  old_help_children = seashcommanddict['help']['children'] 
  # Sets the entire seash command dictionary as 'help' children except itself
  seashcommanddict['help']['children'] = _deep_copy_main_dict(['help'])
  
  for child in old_help_children:
    seashcommanddict['help']['children'][child] = old_help_children[child]

  return seashcommanddict


# Returns the summaries of all children commands to the passed in input_dict. 
def get_command_summaries(input_dict):
  inputdict_mark = input_dict 
  seashdict_mark = seashcommanddict
  
  # Go to one level above the last command node, the last node can be a display 
  # group node.
  while (inputdict_mark[inputdict_mark.keys()[0]]['children']):
    current_command = inputdict_mark.keys()[0]
    # Take 1 step deeper into the commanddict
    seashdict_mark = seashdict_mark[current_command]['children']
    inputdict_mark = inputdict_mark[current_command]['children']
  
  # If it isn't a display group node, then it is a command node.
  # We want to print out its contents.  If we don't do this, we'll end up 
  # printing one level higher than what we intended.
  if inputdict_mark[inputdict_mark.keys()[0]]['name'] != 'display_group':
    # This is a known command identified directly
    if inputdict_mark.keys()[0] in seashdict_mark:
      seashdict_mark = seashdict_mark[inputdict_mark.keys()[0]]['children']
    # This could be a user argument, such as a filename or a target.  These 
    # names wouldn't be in the commanddict directly.  Replace it with an 
    # argument 
    else:  
      for command in seashdict_mark.keys():
        if command.startswith('[') and command.endswith(']'):
          seashdict_mark = seashdict_mark[command]['children']

  # Compile the list of all command summaries with the specified name
  # summaries[commandgroup][module] = [(commandstr, summary), (commandstr, summary), ...]
  summaries = {}
  commandkeys = seashdict_mark.keys()
  commandkeys.sort()  # Display the list in alphabetical order

  for command in commandkeys:
    # Skip user arguments
    if command.startswith('[') and command.endswith(']'):
      continue
    
    # If cmdgroup is unspecified, put the command in the default summary list
    if 'cmdgroup' in seashdict_mark[command]:
      cmdgroup = seashdict_mark[command]['cmdgroup']
    else:
      cmdgroup = ''
    # If a summary is not specified, then treat it as having '' as a summary.
    if 'summary' in seashdict_mark[command]:
      summary = seashdict_mark[command]['summary']
    else:
      summary = ''

    # commandstr is the command that is displayed to the user, with examples
    # e.g. "show ip [to file]" 
    commandstr = command[:]
    if 'example' in seashdict_mark[command]:
      commandstr +=' ' + seashdict_mark[commandstr]['example']
    # If this command is part of a module, mark it as such in the summary
    # e.g. "Shows the longitude and latitude of the node. (geoip module)"
    if 'module' in seashdict_mark[command]:
      module = seashdict_mark[command]['module']
    else:
      module = None
    if not cmdgroup in summaries:
      summaries[cmdgroup] = {}
    if module not in summaries[cmdgroup]:
      summaries[cmdgroup][module] = []
    summaries[cmdgroup][module].append((commandstr, summary))
  return summaries

  
def get_string_from_command_summarylist(command_summarylist, command_string):
  # Command string is the list of commands to list up to that point
  # e.g. for help show info, the command_string would be 'help show'.
  # Find longest commandcchildhild key
  longest_command = ''
  for (command, summary) in command_summarylist:
    if len(command) > len(longest_command):
      longest_command = command

  # Default terminals are often 79 chars wide
  max_linelen = 79
  divider = ' -- '
  max_summary_len = max_linelen - len(longest_command + command_string) - len(divider)
  retstring = ''
  # Resulting string looks like this...
  # show files        -- helptext for show files
  # show ip [to file] -- helptext for show ip
  #                   -- continued...
  # show keys         -- helptext for show keys
  # ...
  formatstr = ('%-'+str(len(longest_command + command_string))
      +'s%'+str(len(divider))+'s'
      +'%s\n')
  for (command, summary) in command_summarylist:
    command = command_string + command
    divider = ' -- '
    while summary:
      # Extract the data to print on this line
      show_this_line = summary[:max_summary_len]
      summary = summary[max_summary_len:]
      # At the point that where we split, if we are in the middle of a word, 
      # backtrack to the closest whitespace and split there
      if (not show_this_line[-1].isspace() and  # char before split point
          summary and  # summary could be empty at this point
          not summary[0].isspace()): # char after split point        
        # Take the last word away from this line and put it back into summary
        last_word = show_this_line.split()[-1]
        show_this_line = show_this_line[:-len(last_word)]
        summary = last_word + summary
      retstring += formatstr % (command, divider, show_this_line)
      # Don't show the command/divider after the first line
      command = ''
      divider = ''
      summary = summary.lstrip()
  return retstring


##### User input parsing related methods #####

"""
seash's command parser:
The parser receives the string of commands the user inputted and proceeds
to iterate through seashcommanddict to verify that the each of the command
string corresponds to a key of seash's command dictionary, and each subsequent 
string corresponds to a command key of the current command dictionary's 
dictionary of children. 

At the same time, a sub-dictionary of seashcommanddict is being built that holds 
only the chain of dictionaries that corresponds to the user's input, with the only
difference being that any user-inputted argument will replace the command key of the 
command dictionary associated with it. Thus, instead of '[TARGET]', the key to the 
command dictionary would instead be '%1'. 

Targets and Group name arguments will be checked to see if the name specified
actually exists, and general Argument command dictionaries with no children will
have the corresponding user input string and any string that follows be spliced
into a single string with spaces in between each word.

A ParseError will be raised if the argument given for Target or Group does not
exist, and also if the user inputted command word does not correspond to any of the
command keys of the current dictionaries of dictionaries the iterator is looking
at and there are no argument keys to suggest the inputted word is an user argument.
"""
def parse_command(userinput, display_parsed_result=False):
  userinput = userinput.strip()
  parsed_input = seash_modules.preprocess_input(userinput)

  # If any modules performed some operation on the user's input, print out the 
  # result here...
  if display_parsed_result and userinput != parsed_input:
    print "Parsed as:", parsed_input

  userinput = parsed_input
  userstringlist = userinput.split()


  # Dictionary of dictionaries that gets built corresponding to user input
  input_dict = {}
  # Iterator that builds the input_dict
  input_dict_builder = input_dict

  # The iterator that runs through the command dictionary
  seash_dict_mark = return_command_dictionary()


  result_string_list = []
  # Cycles through the user's input string by string
  while userstringlist:
    user_string = userstringlist.pop(0)
    # Adds the user string directly to the result string by default.  
    # Some nodes (like the [ARGUMENT] node) need to change what is added to the
    # result string, and they can modify it as needed.

    # For example, if a user types in add %1 to mygroup, %1 and mygroup both
    # will trigger the [GROUP] user argument.  We want %1 and mygroup to be
    # inserted into the result string, not [GROUP].  However, we will use
    # [GROUP] to identify the node. 
    result_string_list.append(user_string)

    # First, an initial check to see if user's input matches a specified command word
    for cmd_pattern in seash_dict_mark.iterkeys():

      if user_string == cmd_pattern or (cmd_pattern in commandvariationdict.keys() and user_string in commandvariationdict[cmd_pattern]):

        # Appends a copy to avoid changing the master list of dictionaries
        input_dict_builder[cmd_pattern] = _shallow_copy(seash_dict_mark[cmd_pattern])

        # Moves the input dictionary builder into the next empty children dictionary
        input_dict_builder = input_dict_builder[cmd_pattern]['children']

        # Iterates into the children dictionary of the next level of command that may follow
        seash_dict_mark = seash_dict_mark[cmd_pattern]['children']

        break


    # If the user's input string does not match the any of the command pattern directly,
    # looks through the command's children for the possibility of being an
    # user inputed argument, generally denoted by starting with a '['
    else:
      for cmd_pattern in seash_dict_mark.iterkeys():

        # Checks if the input is listed as a valid target, and appends
        # the command dictionary to the input_dict
        if cmd_pattern.startswith('['):
          if cmd_pattern == '[TARGET]' or cmd_pattern == '[GROUP]':
            
            # Compares input with current list of targets and/or groups
            # Raise exception if not found in list of targets
            if user_string not in seash_global_variables.targets:
              raise seash_exceptions.ParseError("Target does not exist")
          
          # Necessity of checking existence of keynames yet to be determined
          #elif cmd_pattern == '[KEYNAME]':
          #  pass

          # Necessity of verifying existence of file yet to be determined
          #elif cmd_pattern == '[FILENAME]':
          #  pass
          
          # simply appends to input_dict
          elif cmd_pattern == '[ARGUMENT]':

            # If ARGUMENT doesn't have any children, joins the rest of the user's input
            # into a single string
            if not seash_dict_mark[cmd_pattern]['children']:
              # Take off the current token from the result string list, and then
              # add it to the user string list for concatenation
              userstringlist = [result_string_list.pop()] + userstringlist
              user_string = " ".join(userstringlist)
              # We are now done, we must clear the list to indicate that
              userstringlist = []

              # Resets the user_string as arg_string for consistency in rest of code
              result_string_list.append(user_string)
  

          # Appends a copy of the dictionary to avoid changing the master list of command dictionaries
          # Also sets the name of the target specified by the user as the key of the command's dictionary
          # for later use by the command's callback
          input_dict_builder[user_string] = _shallow_copy(seash_dict_mark[cmd_pattern])
          
          # Sets itself as the recently-added command dictionary's children to be ready to
          # assign the next command dictionary associated with the next user's input string
          input_dict_builder = input_dict_builder[user_string]['children']
            
          # sets the next list of command dictionaries
          seash_dict_mark = seash_dict_mark[cmd_pattern]['children']

          break

      else:
        # If the user command started with 'help', this could be the display keyword.
        # We then append a node that will appear only in the input_dict so that the command parser can 
        # retrieve the display keyword.
        # We use this to determine if a user wanted to show commands in a specific group of commands.
        # e.g. help set, help extended, etc.

        # We need to check for a space after 'help', otherwise a command such as
        # 'helpnonexistent' would be treated as valid, even if 'helpnonexistent'
        # is not in the command dictionary.
        if userinput.startswith('help '):
          input_dict_builder[user_string] = {'name': 'display_group', 'children': {}}

        # If the user input doesn't match any of the pattern words and there's no
        # pattern that suggest it may be a user input argument, raise an exception
        # for going outside of seash's command dictionary
        else:    
          raise seash_exceptions.ParseError("Command not understood")



  return input_dict



"""
seash's command dispatcher:
Taking in the input dictionary of dictionaries, input_dict, the dispatcher iterates
through the series of dictionaries and executes the command callback function of
any command dictionaries that has the key 'priority' while keeping reference of the
last callback function of the command dictionary that had one. After completing
the iteration, if the referenced command callback function has not been executed
already from priority status, the dispatcher proceeds to executes the function. 

Each callback function will be passed a copy of the input_dict for access to 
user-inputted arguments and the environment_dict that keeps track of the current 
state of seash.

A DispatchError will be raised if at the end of the iteration there are no valid command
callbacks to be executed.
"""
def command_dispatch(input_dict, environment_dict):
  
  # Iterator through the user command dictionary
  dict_mark = input_dict


  # Sets the command callback method to be executed
  current_callback = None

  
  # Sets the last 'interrupt' command's callback method that was executed.
  # Used to avoid having current_callback execute the same command function again
  interrupt_callback = None


  # First, general check for any command dictionaries with the 'priority' key
  # Execute the callback methods of those commands
  
  while dict_mark.keys():


    # Pulls out the command word, which also serves as the key to the command's dictionary
    # It should be the only key in the key list of the children's dictionary
    command_key = dict_mark.keys()[0]


    # Sets the callback method reference if command's 'callback' isn't set to None
    if dict_mark[command_key]['callback'] is not None:
      current_callback = dict_mark[command_key]['callback']


    # Executes the callback method of all commands that contains the 'priority' key
    if 'priority' in dict_mark[command_key]:
      interrupt_callback = dict_mark[command_key]['callback']
      interrupt_callback(input_dict.copy(), environment_dict)

      # In the case of 'help', breaks out of the dispatch loop to avoid executing any other
      # command's function
      if command_key == 'help':
        break


    # Iterates into the next dictionary of children commands
    dict_mark = dict_mark[command_key]['children']



  # Raises an exception if current_callback is still None
  if current_callback is None:
    raise seash_exceptions.DispatchError("Invalid command. Please check that the command has been inputted correctly.")


  # Executes current_callback's method if it's not the same one as interrupt_callback
  elif not interrupt_callback == current_callback:
    current_callback(input_dict.copy(), environment_dict)
