"""
Author: Alan Loh
Module: Library of command callback methods. A large portion of the code were
        directly transferred here from the original seash. Each command function 
        is assigned to the appropriate levels of the respective command's 
        dictionary, and are called upon by command_parser.py's dispatch method 
        when executing a user's command input.

All callback methods should take in two arguments: 
-a command dictionary, input_dict, that holds and reflects the user's command input
-the environment_dict holding the following variables:
  host
  port
  expnum 
  filename 
  cmdargs 
  defaulttarget 
  defaultkeyname
  currenttarget
  currentkeyname
  handleinfo
  autosave

In order to pull user-inputed arguments from the command dictionary, the 
following code is used throughout for consistency and ease:

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename input
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

...and command_key will either contain the user's file name, found by searching 
for the appropriate command dictionary with the name 'filename' and taking the 
key associated with it, or it will hold the key of the last command dictionary 
in the input dictionary chain. It is important that the name of the argument 
command dictionary is unique and spelled correctly.

Method names should reflect the expected command string used to executed that 
command dictionary's command callback. For example, the command "show resources
to file"'s method should be called show_resources_to_filename.

Commands with slight variations in function depending on how the user inputted 
it should use a separate method for each variation in its command string. For 
example, 'browse' would have the method named 'browse', while 'browse [type]' 
would have a separate method called 'browse_args'
"""

# For access to additional methods in command handling
import seash_helper
# For access to various global variables kept track of throughout a seash session
import seash_global_variables
# To be able to modify the command dictionary
import seash_dictionary
# To be able to look up what a module commanddict contains (for modulehelp)
import seash_modules

# To be able to throw certain exceptions designed specifically for seash
import seash_exceptions
import seash_modules

import os.path
import sys

# For reverse DNS lookups (of IP address to names)
import socket

# XXX Importing repyportability and dy_import_module's more than 
# XXX once in an import chain overwrites the Repy API calls and 
# XXX disables any overrides (e.g. Affix's). We thus use 
# XXX seash_helper's copy of dylink to pull in the stuff we need.

time = seash_helper.dy_import_module("time.r2py")
rsa = seash_helper.dy_import_module("rsa.r2py")
listops = seash_helper.dy_import_module("listops.r2py")

nmclient = seash_helper.nmclient

# For lookups from Seattle's advertise services
advertise = seash_helper.dy_import_module("advertise.r2py")

# For `loadstate` and `savestate`
serialize = seash_helper.dy_import_module("serialize.r2py")  

# The versions of Seattle that we officially support.
SUPPORTED_PROG_PLATFORMS = ["repyV1", "repyV2"]


# set the target, then handle other operations
def on_target(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's target name
  while input_dict[command_key]['name'] is not 'ontarget':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  if command_key not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error: Unknown target '"+command_key+"'")

  # set the target and strip the rest...
  environment_dict['currenttarget'] = command_key

  # Set default if there's no follow-up commands
  if not input_dict[command_key]['children']:
    environment_dict['defaulttarget'] = environment_dict['currenttarget']




# set the keys, then handle other operations
def as_keyname(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's keyname input
  while input_dict[command_key]['name'] is not 'askeyname':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]


  if command_key not in seash_global_variables.keys:
    raise seash_exceptions.UserError("Error: Unknown identity '"+command_key+"'")

            
  # set the target and strip the rest...
  environment_dict['currentkeyname'] = command_key

  # Set default if there's no follow-up commands
  if not input_dict[command_key]['children']:
    environment_dict['defaultkeyname'] = environment_dict['currentkeyname']



###Show Commands###

# show            -- Does nothing
def show(input_dict, environment_dict):
  pass




# show info       -- Display general information about the vessels
def show_info(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")


  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:

    if seash_global_variables.vesselinfo[longname]['information']:
      print longname, seash_global_variables.vesselinfo[longname]['information']

    else:
      print longname, "has no information (try 'update' or 'list')"




# show targets    -- Display a list of targets
def show_targets(input_dict, environment_dict):

  for target in seash_global_variables.targets:

    if len(seash_global_variables.targets[target]) == 0:
      print target, "(empty)"
      continue

    # this is a vesselentry
    if target == seash_global_variables.targets[target][0]:
      continue

    print target, seash_global_variables.targets[target]



# show groups    -- Display a list of groups 
def show_groups(input_dict, environment_dict):

  for target in seash_global_variables.targets:

    if target == "%all":
      print target, seash_global_variables.targets[target]
      continue
	
    # this is individual target number
    if target.startswith('%'):
      continue
	
    if len(seash_global_variables.targets[target]) == 0:
      print target, seash_global_variables.targets[target]
      continue
	  
    # this is a vesselentry
    if target == seash_global_variables.targets[target][0]:
      continue
	  
    print target, seash_global_variables.targets[target]



# show keys       -- Display the known keys
def show_keys(input_dict, environment_dict):

  for identity in seash_global_variables.keys:

    print identity,seash_global_variables.keys[identity]['publickey'],seash_global_variables.keys[identity]['privatekey']




# show identities -- Display the known identities
def show_identities(input_dict, environment_dict):

  for keyname in seash_global_variables.keys:

    print keyname,

    if seash_global_variables.keys[keyname]['publickey']:
      print "PUB",

    if seash_global_variables.keys[keyname]['privatekey']:
      print "PRIV",

    print




# show users      -- Display the user keys for the vessels
def show_users(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:

    if 'userkeys' in seash_global_variables.vesselinfo[longname]:
      if seash_global_variables.vesselinfo[longname]['userkeys'] == []:
        print longname,"(no keys)"
        continue

      print longname,

      # we'd like to say 'joe's public key' instead of '3453 2323...'
      for key in seash_global_variables.vesselinfo[longname]['userkeys']:

        for identity in seash_global_variables.keys:

          if seash_global_variables.keys[identity]['publickey'] == key:
            print identity,
            break

        else:
          print seash_helper.fit_string(rsa.rsa_publickey_to_string(key), 15),

      print

    else:
      print longname, "has no information (try 'update' or 'list')"
    



# show ownerinfo  -- Display owner information for the vessels
def show_ownerinfo(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:

    if 'ownerinfo' in seash_global_variables.vesselinfo[longname]:
      print longname, "'"+seash_global_variables.vesselinfo[longname]['ownerinfo']+"'"
      # list all of the info...

    else:
      print longname, "has no information (try 'update' or 'list')"




# show advertise  -- Display advertisement information about the vessels
def show_advertise(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:

    if 'advertise' in seash_global_variables.vesselinfo[longname]:

      if seash_global_variables.vesselinfo[longname]['advertise']:
        print longname, "on"

      else:
        print longname, "off"

    # list all of the info...
    else:
      print longname, "has no information (try 'update' or 'list')"




# show owner      -- Display a vessel's owner
def show_owner(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:

    if 'ownerkey' in seash_global_variables.vesselinfo[longname]:
      # we'd like to say 'joe public key' instead of '3453 2323...'
      ownerkey = seash_global_variables.vesselinfo[longname]['ownerkey']

      for identity in seash_global_variables.keys:

        if seash_global_variables.keys[identity]['publickey'] == ownerkey:
          print longname, identity+" pubkey"
          break

      else:
        print longname, seash_helper.fit_string(rsa.rsa_publickey_to_string(ownerkey), 15)

    else:
      print longname, "has no information (try 'update' or 'list')"




# show files      -- Display a list of files in the vessel (*)
def show_files(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  # print the list of files in the vessels (seash method)
  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']], seash_helper.showfiles_target)

  goodlist = []
  faillist = []

  for longname in retdict:

    # True means it worked
    if retdict[longname][0]:
      # let's sort the files...
      fileliststring = retdict[longname][1]
      filelist = fileliststring.split()
      filelist.sort()
      fileliststring = " ".join(filelist)
      print "Files on '"+longname+"': '"+fileliststring+"'"
      goodlist.append(longname)

    else:
      faillist.append(longname)
  
  seash_helper.print_vessel_errors(retdict)

  if goodlist and faillist:
    seash_global_variables.targets['filesgood'] = goodlist
    seash_global_variables.targets['filesfail'] = faillist
    print "Added group 'filesgood' with "+str(len(seash_global_variables.targets['filesgood']))+" targets and 'filesfail' with "+str(len(seash_global_variables.targets['filesfail']))+" targets"




# show log [to file] -- Display the log from the vessel (*)
def show_log(input_dict, environment_dict):

  writeoutputtofile = False


  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  # print the vessel logs...
  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']], seash_helper.showlog_target)

  goodlist = []
  faillist = []

  for longname in retdict:
    # True means it worked
    if retdict[longname][0]:
      if writeoutputtofile:
        # write to a file if requested.
        outputfilename = outputfileprefix +'.'+ longname
        outputfo = file(outputfilename,'w')
        outputfo.write(retdict[longname][1])
        outputfo.close()
        print "Wrote log as '"+outputfilename+"'."

      else:
        # else print it to the terminal
        print "Log from '"+longname+"':"
        print retdict[longname][1]

      # regardless, this is a good node
      goodlist.append(longname)

    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if goodlist and faillist:
    seash_global_variables.targets['loggood'] = goodlist
    seash_global_variables.targets['logfail'] = faillist
    print "Added group 'loggood' with "+str(len(seash_global_variables.targets['loggood']))+" targets and 'logfail' with "+str(len(seash_global_variables.targets['logfail']))+" targets"




# show log to file
def show_log_to_file(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  writeoutputtofile = True
  # handle '~'
  fileandpath = os.path.expanduser(command_key)
  outputfileprefix = fileandpath


  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  # print the vessel logs...
  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']], seash_helper.showlog_target)

  goodlist = []
  faillist = []

  for longname in retdict:
    # True means it worked
    if retdict[longname][0]:
      if writeoutputtofile:
        # write to a file if requested.
        outputfilename = outputfileprefix +'.'+ longname
        outputfo = file(outputfilename,'w')
        outputfo.write(retdict[longname][1])
        outputfo.close()
        print "Wrote log as '"+outputfilename+"'."

      else:
        # else print it to the terminal
        print "Log from '"+longname+"':"
        print retdict[longname][1]

      # regardless, this is a good node
      goodlist.append(longname)

    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if goodlist and faillist:
    seash_global_variables.targets['loggood'] = goodlist
    seash_global_variables.targets['logfail'] = faillist
    print "Added group 'loggood' with "+str(len(seash_global_variables.targets['loggood']))+" targets and 'logfail' with "+str(len(seash_global_variables.targets['logfail']))+" targets"




# show resources  -- Display the resources / restrictions for the vessel (*)
def show_resources(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']], seash_helper.showresources_target)
  faillist = []
  goodlist = []

  for longname in retdict:

    # True means it worked
    if retdict[longname][0]:
      print "Resource data for '"+longname+"':"
      print retdict[longname][1]
      goodlist.append(longname)

    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if goodlist and faillist:
    seash_global_variables.targets['resourcegood'] = goodlist
    seash_global_variables.targets['resourcefail'] = faillist
    print "Added group 'resourcegood' with "+str(len(seash_global_variables.targets['resourcegood']))+" targets and 'resourcefail' with "+str(len(seash_global_variables.targets['resourcefail']))+" targets"




# show offcut     -- Display the offcut resource for the node (*)
def show_offcut(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")


  # we should only visit a node once...
  nodelist = listops.listops_uniq(seash_helper.longnamelist_to_nodelist(seash_global_variables.targets[environment_dict['currenttarget']]))
  retdict = seash_helper.contact_targets(nodelist, seash_helper.showoffcut_target)

  for nodename in retdict:

    if retdict[nodename][0]:
      print "Offcut resource data for '"+nodename+"':"
      print retdict[nodename][1]

  seash_helper.print_vessel_errors(retdict)




# show ip [to file] -- Display the ip addresses of the nodes
def show_ip(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  # print to the terminal (stdout)
  # write data here...
  outfo = sys.stdout


  # we should only visit a node once...
  printedIPlist = []

  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:
    thisnodeIP = seash_global_variables.vesselinfo[longname]['IP']

    if thisnodeIP not in printedIPlist:
      printedIPlist.append(thisnodeIP)
      print >> outfo, thisnodeIP




# show ip to file
def show_ip_to_file(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  outfo = open(command_key,"w+")


  # we should only visit a node once...
  printedIPlist = []

  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:
    thisnodeIP = seash_global_variables.vesselinfo[longname]['IP']

    if thisnodeIP not in printedIPlist:
      printedIPlist.append(thisnodeIP)
      print >> outfo, thisnodeIP

  # if it's a file, close it...
  outfo.close()




# show hostname        -- Display the hostnames of the nodes
def show_hostname(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Error, command requires a target")


  # we should only visit a node once...
  printedIPlist = []

  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:
    thisnodeIP = seash_global_variables.vesselinfo[longname]['IP']

    if thisnodeIP not in printedIPlist:
      printedIPlist.append(thisnodeIP)
      print thisnodeIP,

      try: 
        nodeinfo = socket.gethostbyaddr(thisnodeIP)

      except (socket.herror,socket.gaierror, socket.timeout, socket.error):
        print 'has unknown host information'

      else:
        print 'is known as',nodeinfo[0]







# show timeout    -- Display the timeout for nodes
def show_timeout(input_dict, environment_dict):
  print seash_global_variables.globalseashtimeout




# show uploadrate    -- Display the file upload rate
def show_uploadrate(input_dict, environment_dict):
  print seash_global_variables.globaluploadrate




# add target (to group)
def add_target(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's target name
  while input_dict[command_key]['name'] is not 'target':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  source = command_key
  dest = environment_dict['currenttarget']


  # okay, now source and dest are set.   Time to add the nodes in source
  # to the group dest...
  if source not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown target '"+source+"'")

  if dest not in seash_global_variables.targets:
    if not seash_helper.valid_targetname(dest):
      raise seash_exceptions.UserError("Error, invalid target name '"+dest+"'")
    seash_global_variables.targets[dest] = []

  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError("Can't modify the contents of '"+dest+"'")

  # source - dest has what we should add (items in source but not dest)
  addlist = listops.listops_difference(seash_global_variables.targets[source],seash_global_variables.targets[dest])

  if len(addlist) == 0:
    raise seash_exceptions.UserError("No targets to add (the target is already in '"+dest+"')")

  for item in addlist:
    seash_global_variables.targets[dest].append(item)




# add target to group
def add_target_to_group(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's target name
  while input_dict[command_key]['name'] is not 'target':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  source = command_key

  # Iterates through the dictionary to retrieve the user's group argument
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  dest = command_key


  # okay, now source and dest are set.   Time to add the nodes in source
  # to the group dest...
  if source not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown target '"+source+"'")

  if dest not in seash_global_variables.targets:
    if not seash_helper.valid_targetname(dest):
      raise seash_exceptions.UserError("Error, invalid target name '"+dest+"'")

    seash_global_variables.targets[dest] = []

  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError("Can't modify the contents of '"+dest+"'")

  # source - dest has what we should add (items in source but not dest)
  addlist = listops.listops_difference(seash_global_variables.targets[source],seash_global_variables.targets[dest])

  if len(addlist) == 0:
    raise seash_exceptions.UserError("No targets to add (the target is already in '"+dest+"')")

  for item in addlist:
    seash_global_variables.targets[dest].append(item)





# add to group
def add_to_group(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's group argument
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  source = environment_dict['currenttarget']
  dest = command_key


  # okay, now source and dest are set.   Time to add the nodes in source
  # to the group dest...
  if source not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown target '"+source+"'")

  if dest not in seash_global_variables.targets:
    if not seash_helper.valid_targetname(dest):
      raise seash_exceptions.UserError("Error, invalid target name '"+dest+"'")
    seash_global_variables.targets[dest] = []

  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError("Can't modify the contents of '"+dest+"'")

  # source - dest has what we should add (items in source but not dest)
  addlist = listops.listops_difference(seash_global_variables.targets[source],seash_global_variables.targets[dest])

  if len(addlist) == 0:
    raise seash_exceptions.UserError("No targets to add (the target is already in '"+dest+"')")

  for item in addlist:
    seash_global_variables.targets[dest].append(item)





# remove target (from group)
def remove_target(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's target name
  while input_dict[command_key]['name'] is not 'target':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  source = command_key
  dest = environment_dict['currenttarget']



  # time to check args and do the ops
  if source not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown target '"+source+"'")

  if dest not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown group '"+dest+"'")

  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError("Can't modify the contents of '"+dest+"'")

  # find the items to remove (the items in both dest and source)
  removelist = listops.listops_intersect(seash_global_variables.targets[dest],seash_global_variables.targets[source])

  if len(removelist) == 0:
    raise seash_exceptions.UserError("No targets to remove (no items from '"+source+"' are in '"+dest+"')")

  # it's okay to end up with an empty group.   We'll leave it...
  for item in removelist:
    seash_global_variables.targets[dest].remove(item)




# remove target from group
def remove_target_from_group(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's target name
  while input_dict[command_key]['name'] is not 'target':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  source = command_key

  # Iterates through the dictionary to retrieve the user's group name
  while input_dict[command_key]['name'] is not 'group':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  dest = command_key


  # time to check args and do the ops
  if source not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown target '"+source+"'")

  if dest not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown group '"+dest+"'")

  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError("Can't modify the contents of '"+dest+"'")

  # find the items to remove (the items in both dest and source)
  removelist = listops.listops_intersect(seash_global_variables.targets[dest],seash_global_variables.targets[source])

  if len(removelist) == 0:
    raise seash_exceptions.UserError("No targets to remove (no items from '"+source+"' are in '"+dest+"')")

  # it's okay to end up with an empty group.   We'll leave it...
  for item in removelist:
    seash_global_variables.targets[dest].remove(item)




# remove from group
def remove_from_group(input_dict, environment_dict):

  source = environment_dict['currenttarget']

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's group name
  while input_dict[command_key]['name'] is not 'group':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  dest = command_key


  # time to check args and do the ops
  if source not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown target '"+source+"'")

  if dest not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown group '"+dest+"'")

  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError("Can't modify the contents of '"+dest+"'")

  # find the items to remove (the items in both dest and source)
  removelist = listops.listops_intersect(seash_global_variables.targets[dest],seash_global_variables.targets[source])

  if len(removelist) == 0:
    raise seash_exceptions.UserError("No targets to remove (no items from '"+source+"' are in '"+dest+"')")

  # it's okay to end up with an empty group.   We'll leave it...
  for item in removelist:
    seash_global_variables.targets[dest].remove(item)




# move target to group
def move_target_to_group(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's target name
  while input_dict[command_key]['name'] is not 'target':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  moving = command_key
  source = environment_dict['currenttarget']

  # Iterates through the dictionary to retrieve the user's group name
  while input_dict[command_key]['name'] is not 'group':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  dest = command_key


  # check args...
  if source not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown group '"+source+"'")

  if moving not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown group '"+moving+"'")

  if dest not in seash_global_variables.targets:
    raise seash_exceptions.UserError("Error, unknown group '"+dest+"'")


  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError("Can't modify the contents of '"+source+"'")

  if seash_helper.is_immutable_targetname(dest):
    raise seash_exceptions.UserError( "Can't modify the contents of '"+dest+"'")

  removelist = listops.listops_intersect(seash_global_variables.targets[source], seash_global_variables.targets[moving])
  if len(removelist) == 0:
    raise seash_exceptions.UserError("Error, '"+moving+"' is not in '"+source+"'")

  addlist = listops.listops_difference(removelist, seash_global_variables.targets[dest])
  if len(addlist) == 0:
    raise seash_exceptions.UserError("Error, the common items between '"+source+"' and '"+moving+"' are already in '"+dest+"'")

  for item in removelist:
    seash_global_variables.targets[source].remove(item)

  for item in addlist:
    seash_global_variables.targets[dest].append(item)








# contact host:port[:vessel] -- Communicate with a node
def contact(input_dict, environment_dict):

  if environment_dict['currentkeyname'] == None or not seash_global_variables.keys[environment_dict['currentkeyname']]['publickey']:
    raise seash_exceptions.UserError("Error, must contact as an identity")

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  if len(command_key.split(':')) == 2:
    environment_dict['host'], portstring = command_key.split(':')
    environment_dict['port'] = int(portstring)
    vesselname = None

  elif len(command_key.split(':')) == 3:
    environment_dict['host'], portstring,vesselname = command_key.split(':')
    environment_dict['port'] = int(portstring)

  else:
    raise seash_exceptions.UserError("Error, usage is contact host:port[:vessel]")


  # get information about the node's vessels
  thishandle = nmclient.nmclient_createhandle(environment_dict['host'], environment_dict['port'], privatekey = seash_global_variables.keys[environment_dict['currentkeyname']]['privatekey'], publickey = seash_global_variables.keys[environment_dict['currentkeyname']]['publickey'], vesselid = vesselname, timeout = seash_global_variables.globalseashtimeout)
  ownervessels, uservessels = nmclient.nmclient_listaccessiblevessels(thishandle,seash_global_variables.keys[environment_dict['currentkeyname']]['publickey'])

  newidlist = []
  # determine if we control the specified vessel...
  if vesselname:
    if vesselname in ownervessels or vesselname in uservessels:
      longname = environment_dict['host']+":"+str(environment_dict['port'])+":"+vesselname
      # no need to set the vesselname, we did so above...
      id = seash_helper.add_vessel(longname,environment_dict['currentkeyname'],thishandle)
      newidlist.append('%'+str(id)+"("+longname+")")

    else:
      raise seash_exceptions.UserError("Error, cannot access vessel '"+vesselname+"'")

  # we should add anything we can access
  else:
    for vesselname in ownervessels:

      longname = environment_dict['host']+":"+str(environment_dict['port'])+":"+vesselname

      if longname not in seash_global_variables.targets:
        # set the vesselname
        # NOTE: we leak handles (no cleanup of thishandle).   
        # I think we don't care...
        newhandle = nmclient.nmclient_duplicatehandle(thishandle)
        environment_dict['handleinfo'] = nmclient.nmclient_get_handle_info(newhandle)
        environment_dict['handleinfo']['vesselname'] = vesselname
        nmclient.nmclient_set_handle_info(newhandle, environment_dict['handleinfo'])

        id = seash_helper.add_vessel(longname,environment_dict['currentkeyname'],newhandle)
        newidlist.append('%'+str(id)+"("+longname+")")


    for vesselname in uservessels:

      longname = environment_dict['host']+":"+str(environment_dict['port'])+":"+vesselname

      if longname not in seash_global_variables.targets:
        # set the vesselname
        # NOTE: we leak handles (no cleanup of thishandle).   
        # I think we don't care...
        newhandle = nmclient.nmclient_duplicatehandle(thishandle)
        environment_dict['handleinfo'] = nmclient.nmclient_get_handle_info(newhandle)
        environment_dict['handleinfo']['vesselname'] = vesselname
        nmclient.nmclient_set_handle_info(newhandle, environment_dict['handleinfo'])

        id = seash_helper.add_vessel(longname,environment_dict['currentkeyname'],newhandle)
        newidlist.append('%'+str(id)+"("+longname+")")


  # tell the user what we did...
  if len(newidlist) == 0:
    print "Could not add any targets."

  else:
    print "Added targets: "+", ".join(newidlist)
            
  





# browse                               -- Find experiments I can control
def browse(input_dict, environment_dict):
 
  if environment_dict['currentkeyname'] == None or not seash_global_variables.keys[environment_dict['currentkeyname']]['publickey']:
    raise seash_exceptions.UserError("Error, must browse as an identity with a public key")


  try:
    nodelist = advertise.advertise_lookup(seash_global_variables.keys[environment_dict['currentkeyname']]['publickey'], graceperiod = 3)
  except (advertise.AdvertiseError, TimeoutError), e:
    # print the error and return to the user.   Let them decide what to do.
    print "Error:",e
    print "Retry or check network connection."
    return
    


  # If there are no vessels for a user, the lookup may return ''
  for nodename in nodelist[:]:
    if nodename == '':
      nodelist.remove(nodename)

  # we'll output a message about the new keys later...
  newidlist = []

  faillist = []

  seash_global_variables.targets['browsegood'] = []

  print nodelist

  # currently, if I browse more than once, I look up everything again...
  retdict = seash_helper.contact_targets(nodelist,seash_helper.browse_target, environment_dict['currentkeyname'])

  # parse the output so we can print out something intelligible
  for nodename in retdict:

    if retdict[nodename][0]:
      newidlist = newidlist + retdict[nodename][1]

    else:
      faillist.append(nodename)

  seash_helper.print_vessel_errors(retdict)

  if len(newidlist) == 0:
    print "Could not add any new targets."
  else:
    print "Added targets: "+", ".join(newidlist)

  if len(seash_global_variables.targets['browsegood']) > 0:
    print "Added group 'browsegood' with "+str(len(seash_global_variables.targets['browsegood']))+" targets"



# browse [arg]
def browse_arg(input_dict, environment_dict):

  if environment_dict['currentkeyname'] == None or not seash_global_variables.keys[environment_dict['currentkeyname']]['publickey']:
    raise seash_exceptions.UserError("Error, must browse as an identity with a public key")


  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument input
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  type_list = command_key.split()


  try:
    # they are trying to only do some types of lookup...
    nodelist = advertise.advertise_lookup(seash_global_variables.keys[environment_dict['currentkeyname']]['publickey'],lookuptype=type_list)
  except (advertise.AdvertiseError, TimeoutError), e:
    # print the error and return to the user.   Let them decide what to do.
    print "Error:",e
    print "Retry or check network connection."
    return
    


  # If there are no vessels for a user, the lookup may return ''
  for nodename in nodelist[:]:
    if nodename == '':
      nodelist.remove(nodename)

  # we'll output a message about the new keys later...
  newidlist = []

  faillist = []

  seash_global_variables.targets['browsegood'] = []

  print nodelist
  # currently, if I browse more than once, I look up everything again...
  retdict = seash_helper.contact_targets(nodelist,seash_helper.browse_target, environment_dict['currentkeyname'])

  # parse the output so we can print out something intelligible
  for nodename in retdict:

    if retdict[nodename][0]:
      newidlist = newidlist + retdict[nodename][1]

  seash_helper.print_vessel_errors(retdict)

  if len(newidlist) == 0:
    print "Could not add any new targets."
  else:
    print "Added targets: "+", ".join(newidlist)

  if len(seash_global_variables.targets['browsegood']) > 0:
    print "Added group 'browsegood' with "+str(len(seash_global_variables.targets['browsegood']))+" targets"




# genkeys filename                             -- creates keys
def genkeys_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename input
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  keylength = 1024
  # expand '~'
  fileandpath = os.path.expanduser(command_key)
  keyname = os.path.basename(fileandpath)
  pubkeyfn = fileandpath+'.publickey'
  privkeyfn = fileandpath+'.privatekey'

  # RepyV2's API does not allow us to truncate a file in-place.
  # Therefore, we need to make sure we're creating a new file, otherwise
  # the contents of the public/private key files that we create will be
  # corrupt.

  seash_helper.remove_files([pubkeyfn, privkeyfn])

  # do the actual generation (will take a while)
  newkeys = rsa.rsa_gen_pubpriv_keys(keylength)

  rsa.rsa_privatekey_to_file(newkeys[1], privkeyfn)
  rsa.rsa_publickey_to_file(newkeys[0], pubkeyfn)
  seash_global_variables.keys[keyname] = {'publickey': newkeys[0], 
      'privatekey': newkeys[1]}

  print "Created identity '"+keyname+"'"




# genkeys filename [len]
def genkeys_filename_len(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename input
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  # expand '~'
  fileandpath = os.path.expanduser(command_key)
  keyname = os.path.basename(fileandpath)
  pubkeyfn = fileandpath + '.publickey'
  privkeyfn = fileandpath + '.privatekey'


  # Iterates through the dictionary to retrieve the user's length argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  keylength = int(command_key)


  # do the actual generation (will take a while)
  newkeys = rsa.rsa_gen_pubpriv_keys(keylength)

  # RepyV2's API does not allow us to truncate a file in-place.
  # Therefore, we need to make sure we're creating a new file, otherwise
  # the contents of the public/private key files that we create will be
  # corrupt.

  seash_helper.remove_files([pubkeyfn, privkeyfn])

  rsa.rsa_privatekey_to_file(newkeys[1], privkeyfn)
  rsa.rsa_publickey_to_file(newkeys[0], pubkeyfn)
  seash_global_variables.keys[keyname] = {'publickey': newkeys[0], 
      'privatekey': newkeys[1]}

  print "Created identity '"+keyname+"'"




# genkeys filename [len] [as identity]
def genkeys_filename_len_as_identity(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename input
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  pubkeyfn = command_key + '.publickey'
  privkeyfn = command_key + '.privatekey'


  # Iterates through the dictionary to retrieve the user's length argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  keylength = int(command_key)


  # Iterates through the dictionary to retrieve the user's keyname argument
  while input_dict[command_key]['name'] is not 'keyname':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  keyname = command_key


  # do the actual generation (will take a while)
  newkeys = rsa.rsa_gen_pubpriv_keys(keylength)

  # RepyV2's API does not allow us to truncate a file in-place.
  # Therefore, we need to make sure we're creating a new file, otherwise
  # the contents of the public/private key files that we create will be
  # corrupt.

  seash_helper.remove_files([pubkeyfn, privkeyfn])

  rsa.rsa_privatekey_to_file(newkeys[1], privkeyfn)
  rsa.rsa_publickey_to_file(newkeys[0], pubkeyfn)
  seash_global_variables.keys[keyname] = {'publickey': newkeys[0], 
      'privatekey': newkeys[1]}

  print "Created identity '" + keyname + "'"




# genkeys filename [as identity]
def genkeys_filename_as_identity(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename input
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  keylength = 1024
  pubkeyfn = command_key + '.publickey'
  privkeyfn = command_key + '.privatekey'


  # Iterates through the dictionary to retrieve the user's keyname argument
  while input_dict[command_key]['name'] is not 'keyname':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  keyname = command_key

  # do the actual generation (will take a while)
  newkeys = rsa.rsa_gen_pubpriv_keys(keylength)

  # RepyV2's API does not allow us to truncate a file in-place.
  # Therefore, we need to make sure we're creating a new file, otherwise
  # the contents of the public/private key files that we create will be
  # corrupt.

  seash_helper.remove_files([pubkeyfn, privkeyfn])

  rsa.rsa_privatekey_to_file(newkeys[1], privkeyfn)
  rsa.rsa_publickey_to_file(newkeys[0], pubkeyfn)
  seash_global_variables.keys[keyname] = {'publickey':newkeys[0], 'privatekey':newkeys[1]}

  print "Created identity '"+keyname+"'"
  




# loadpub filename [as identity]                    -- loads a public key
def loadpub_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  # they typed 'loadpub foo.publickey'
  if command_key.endswith('.publickey'):
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    keyname = os.path.basename(fileandpath[:len('.publickey')])
    pubkeyfn = fileandpath
  else:
    # they typed 'loadpub foo'
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    keyname = os.path.basename(fileandpath)
    pubkeyfn = fileandpath+'.publickey'

  # load the key and update the table...
  pubkey = rsa.rsa_file_to_publickey(pubkeyfn)

  if keyname not in seash_global_variables.keys:
    seash_global_variables.keys[keyname] = {'publickey': pubkey, 
        'privatekey':None}
  else:
    seash_global_variables.keys[keyname]['publickey'] = pubkey

    # Check the keys, on error reverse the change and re-raise
    try:
      seash_helper.check_key_set(keyname)

    except:
      seash_global_variables.keys[keyname]['publickey'] = None
      raise




# loadpub keyname as identity
def loadpub_filename_as(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  # they typed 'loadpub foo.publickey'
  if command_key.endswith('.publickey'):
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    pubkeyfn = fileandpath
  else:
    # they typed 'loadpub foo'
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    pubkeyfn = fileandpath+'.publickey'

# Iterates through the dictionary to retrieve the user's keyname argument
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  keyname = command_key

  # load the key and update the table...
  pubkey = rsa.rsa_file_to_publickey(pubkeyfn)
  if keyname not in seash_global_variables.keys:
    seash_global_variables.keys[keyname] = {'publickey':pubkey, 'privatekey':None}
  else:
    seash_global_variables.keys[keyname]['publickey'] = pubkey

    # Check the keys, on error reverse the change and re-raise
    try:
      seash_helper.check_key_set(keyname)
    except:
      seash_global_variables.keys[keyname]['publickey'] = None
      raise




# loadpriv filename [as identity]                    -- loads a private key
def loadpriv_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  # they typed 'loadpriv foo.privatekey'
  if command_key.endswith('.privatekey'):
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    privkeyfn = fileandpath + '.privatekey'
    keyname = os.path.basename(fileandpath[:len('.privatekey')])
  else:
    # they typed 'loadpriv foo'
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    privkeyfn = fileandpath + '.privatekey'
    keyname = os.path.basename(fileandpath)


  # load the key and update the table...
  privkey = rsa.rsa_file_to_privatekey(privkeyfn)
  if keyname not in seash_global_variables.keys:
    seash_global_variables.keys[keyname] = {'privatekey': privkey, 
        'publickey': None}
  else:
    seash_global_variables.keys[keyname]['privatekey'] = privkey

    # Check the keys, on error reverse the change and re-raise
    try:
      seash_helper.check_key_set(keyname)
    except:
      seash_global_variables.keys[keyname]['privatekey'] = None
      raise
          



# loadpriv filename as identity
def loadpriv_filename_as(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  # they typed 'loadpriv foo.privatekey'
  if command_key.endswith('.privatekey'):
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    privkeyfn = fileandpath
  else:
    # they typed 'loadpriv foo'
    # handle '~'
    fileandpath = os.path.expanduser(command_key)
    privkeyfn = fileandpath+'.publickey'

  # Iterates through the dictionary to retrieve the user's keyname argument
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  keyname = command_key


  # load the key and update the table...
  privkey = rsa.rsa_file_to_privatekey(privkeyfn)
  if keyname not in seash_global_variables.keys:
    seash_global_variables.keys[keyname] = {'privatekey': privkey, 
        'publickey': None}
  else:
    seash_global_variables.keys[keyname]['privatekey'] = privkey

    # Check the keys, on error reverse the change and re-raise
    try:
      seash_helper.check_key_set(keyname)
    except:
      seash_global_variables.keys[keyname]['privatekey'] = None
      raise




# loadkeys filename [as identity]                    -- loads a private key
def loadkeys_keyname(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  if command_key.endswith('publickey') or command_key.endswith('privatekey'):
    print 'Warning: Trying to load a keypair named',
    print '"' + command_key + '.publickey" and "' + command_key + '.privatekey"'


  # the user input may have a directory or tilde in it.   The key name 
  # shouldn't have either.
  fileandpath = os.path.expanduser(command_key)
  keyname = os.path.basename(fileandpath)
  privkeyfn = fileandpath + '.privatekey'
  pubkeyfn = fileandpath + '.publickey'




  # load the keys and update the table...
  try:
    privkey = rsa.rsa_file_to_privatekey(privkeyfn)
  except (OSError, IOError), e:
    raise seash_exceptions.UserError("Cannot locate private key '" + 
        privkeyfn + "'.\nDetailed error: '" + str(e) + "'.")

  try:
    pubkey = rsa.rsa_file_to_publickey(pubkeyfn)
  except (OSError, IOError), e:
    raise seash_exceptions.UserError("Cannot locate private key '" + 
        privkeyfn + "'.\nDetailed error: '" + str(e) + "'.")

  seash_global_variables.keys[keyname] = {'privatekey': privkey, 
      'publickey': pubkey}


  # Check the keys, on error reverse the change and re-raise
  try:
    seash_helper.check_key_set(keyname)
  except:
    del seash_global_variables.keys[keyname]
    raise




# loadkeys keyname as identity
def loadkeys_keyname_as(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  if command_key.endswith('publickey') or command_key.endswith('privatekey'):
    print 'Warning: Trying to load a keypair named "'+command_key+'.publickey" and "'+command_key+'.privatekey"'


  # the user input may have a directory or tilde in it.   The key name 
  # shouldn't have either.
  fileandpath = os.path.expanduser(command_key)
  privkeyfn = fileandpath+'.privatekey'
  pubkeyfn = fileandpath+'.publickey'
  

  # Iterates through the dictionary to retrieve the user's keyname argument
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  keyname = command_key


  # load the keys and update the table...
  try:
    privkey = rsa.rsa_file_to_privatekey(privkeyfn)
  except (OSError, IOError), e:
    raise seash_exceptions.UserError("Cannot locate private key '" + 
        privkeyfn + "'.\nDetailed error: '" + str(e) + "'.")

  try:
    pubkey = rsa.rsa_file_to_publickey(pubkeyfn)
  except (OSError, IOError), e:
    raise seash_exceptions.UserError("Cannot locate public key '" + 
        pubkeyfn + "'.\nDetailed error: '" + str(e) + "'.")

  seash_global_variables.keys[keyname] = {'privatekey': privkey, 
      'publickey': pubkey}


  # Check the keys, on error reverse the change and re-raise
  try:
    seash_helper.check_key_set(keyname)
  except:
    del seash_global_variables.keys[keyname]
    raise



"""
 list               -- Update and display information about the vessels

 output looks similar to:
  ID Own                       Name     Status              Owner Information
  %1  *       128.208.3.173:1224:v5      Fresh                               
  %2  *        128.208.3.86:1224:v2      Fresh                               
  %3          234.17.98.23:53322:v5    Stopped               Chord experiment

"""
def list(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  # update information about the vessels...
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.list_or_update_target)

  for longname in retdict:

    if retdict[longname][0]:
      goodlist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if goodlist:
    print "%4s %3s %25s %10s %30s" % ('ID','Own','Name','Status','Owner Information')

  # walk through target to print instead of the good list so that the
  # names are printed in order...
  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:

    if longname in goodlist:  
      if seash_global_variables.keys[environment_dict['currentkeyname']]['publickey'] == seash_global_variables.vesselinfo[longname]['ownerkey']:
        owner = '*'
      else:
        owner = ''
      print "%4s  %1s  %25s %10s %30s" % (seash_global_variables.vesselinfo[longname]['ID'],owner,seash_helper.fit_string(longname,25),seash_global_variables.vesselinfo[longname]['status'],seash_helper.fit_string(seash_global_variables.vesselinfo[longname]['ownerinfo'],30))

  # add groups for fail and good (if there is a difference in what nodes do)
  if goodlist and faillist:
    seash_global_variables.targets['listgood'] = goodlist
    seash_global_variables.targets['listfail'] = faillist
    print "Added group 'listgood' with "+str(len(seash_global_variables.targets['listgood']))+" targets and 'listfail' with "+str(len(seash_global_variables.targets['listfail']))+" targets"


  statusdict = {}
  # add status groups (if there is a difference in vessel state)
  for longname in goodlist:
    if seash_global_variables.vesselinfo[longname]['status'] not in statusdict:
      # create a list with this element...
      statusdict[seash_global_variables.vesselinfo[longname]['status']] = []
    statusdict[seash_global_variables.vesselinfo[longname]['status']].append(longname)

  if len(statusdict) > 1:
    print "Added group",
    for statusname in statusdict:
      seash_global_variables.targets['list'+statusname] = statusdict[statusname]
      print "'list"+statusname+"' with "+str(len(seash_global_variables.targets['list'+statusname]))+" targets",
    print
          

  
# reset                  -- Reset the vessel (clear the log and files and stop)
def reset(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  # reset the vessels...
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.reset_target)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  # and display it...
  seash_helper.print_vessel_errors(retdict)

  if goodlist and faillist:
    seash_global_variables.targets['resetgood'] = goodlist
    seash_global_variables.targets['resetfail'] = faillist
    print "Added group 'resetgood' with "+str(len(seash_global_variables.targets['resetgood']))+" targets and 'resetfail' with "+str(len(seash_global_variables.targets['resetfail']))+" targets"


  



# update
def update(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  # update information about the vessels...
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.list_or_update_target)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if goodlist and faillist:
    seash_global_variables.targets['updategood'] = goodlist
    seash_global_variables.targets['updatefail'] = faillist
    print "Added group 'updategood' with "+str(len(seash_global_variables.targets['updategood']))+" targets and 'updatefail' with "+str(len(seash_global_variables.targets['updatefail']))+" targets"

  


# savestate localfile -- Save current states to file (Added by Danny Y. Huang)
def savestate_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  # expand ~
  fileandpath = os.path.expanduser(command_key) 

  try:
    seash_helper.savestate(fileandpath, environment_dict['handleinfo'], 
                           environment_dict['host'], environment_dict['port'], 
                           environment_dict['expnum'], environment_dict['filename'], 
                           environment_dict['cmdargs'], environment_dict['defaulttarget'], 
                           environment_dict['defaultkeyname'], environment_dict['autosave'], 
                           environment_dict['currentkeyname'])
  except Exception, error:
    raise seash_exceptions.UserError("Error saving state: '" + str(error) + "'.")





# loadstate localfile -- Load states from file (Added by Danny Y. Huang)
def loadstate_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  # expand ~
  fileandpath = os.path.expanduser(command_key) 

  if not environment_dict['currentkeyname']:
    raise seash_exceptions.UserError("Specify the key name by first typing 'as [username]'.")

  # reading encrypted serialized states from file
  state_obj = open(fileandpath, 'r')
  cypher = state_obj.read()
  state_obj.close()

  try:
    # decrypt states
    statestr = rsa.rsa_decrypt(cypher, seash_global_variables.keys[environment_dict['currentkeyname']]['privatekey'])

    # deserialize
    state = serialize.serialize_deserializedata(statestr)
  except Exception, error:
    error_msg = "Unable to correctly parse state file. Your private "
    error_msg += "key may be incorrect."
    raise seash_exceptions.UserError(error_msg)

  # restore variables
  seash_global_variables.targets = state['targets']
  seash_global_variables.keys = state['keys']
  seash_global_variables.vesselinfo = state['vesselinfo']
  environment_dict['handleinfo'] = state['handleinfo']
  seash_global_variables.nextid = state['nextid']
  environment_dict['host'] = state['host']
  environment_dict['port'] = state['port']
  environment_dict['expnum'] = state['expnum']
  environment_dict['filename'] = state['filename']
  environment_dict['cmdargs'] = state['cmdargs'] 
  environment_dict['defaulttarget'] = state['defaulttarget']
  environment_dict['defaultkeyname'] = state['defaultkeyname']
  environment_dict['autosave'] = state['autosave']
  seash_global_variables.globalseashtimeout = state['globalseashtimeout']
  seash_global_variables.globaluploadrate = state['globaluploadrate']

  # Reload node handles. Rogue nodes are deleted from the original targets
  # and vesselinfo dictionaries.
  retdict = seash_helper.contact_targets(seash_global_variables.targets['%all'], seash_helper.reload_target, environment_dict['handleinfo'])

  reloadgood = []
  reloadfail = []

  for longname in retdict:
    if not retdict[longname][0]:
      reloadfail.append(longname)
    else:
      reloadgood.append(longname)
      
  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if reloadfail and reloadgood:
    seash_global_variables.targets['reloadgood'] = reloadgood
    seash_global_variables.targets['reloadfail'] = reloadfail
    print("Added group 'reloadgood' with " +str(len(seash_global_variables.targets['reloadgood'])) + \
            " targets and 'reloadfail' with " + str(len(seash_global_variables.targets['reloadfail'])) + " targets")

  if environment_dict['autosave']:
    print "Autosave is on."






# upload localfn (remotefn)   -- Upload a file 
def upload_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]


  # expand '~'
  fileandpath = os.path.expanduser(command_key)
  remotefn = os.path.basename(fileandpath)
  localfn = fileandpath


  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")


  # read the local file...
  fileobj = open(localfn,"r")
  filedata = fileobj.read()
  fileobj.close()


  # to prevent timeouts during file uploads on slow connections,
  # temporarily sets the timeout count on all vessels to be the
  # time needed to upload the file with the current globaluploadrate
  seash_helper.set_upload_timeout(filedata)


  # add the file to the vessels...
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.upload_target, remotefn, filedata)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['uploadgood'] = goodlist
    seash_global_variables.targets['uploadfail'] = faillist
    print "Added group 'uploadgood' with "+str(len(seash_global_variables.targets['uploadgood']))+" targets and 'uploadfail' with "+str(len(seash_global_variables.targets['uploadfail']))+" targets"


  # resets the timeout count on all vessels to globalseashtimeout
  seash_helper.reset_vessel_timeout()




# upload localfn remotefn
def upload_filename_remotefn(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  # expand '~'
  fileandpath = os.path.expanduser(command_key)
  localfn = fileandpath

  # Iterates through the dictionary to retrieve the user's argument input
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  remotefn = command_key


  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")


  # read the local file...
  fileobj = open(localfn,"r")
  filedata = fileobj.read()
  fileobj.close()


  # to prevent timeouts during file uploads on slow connections,
  # temporarily sets the timeout count on all vessels to be the
  # time needed to upload the file with the current globaluploadrate
  seash_helper.set_upload_timeout(filedata)


  # add the file to the vessels...
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.upload_target, remotefn, filedata)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['uploadgood'] = goodlist
    seash_global_variables.targets['uploadfail'] = faillist
    print "Added group 'uploadgood' with "+str(len(seash_global_variables.targets['uploadgood']))+" targets and 'uploadfail' with "+str(len(seash_global_variables.targets['uploadfail']))+" targets"


  # resets the timeout count on all vessels to globalseashtimeout
  seash_helper.reset_vessel_timeout()
  



# download remotefn (localfn) -- Download a file 
def download_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  # handle '~'
  fileandpath = os.path.expanduser(command_key)
  remotefn = os.path.basename(fileandpath)
  localfn = fileandpath

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")



  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.download_target,localfn,remotefn)

  writestring = ''

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
      # for output...
      writestring = writestring + retdict[longname][1]+ " "
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if writestring:
    print "Wrote files: "+writestring

  # add groups if needed...
  if goodlist and faillist:
    seash_global_variables.targets['downloadgood'] = goodlist
    seash_global_variables.targets['downloadfail'] = faillist
    print "Added group 'downloadgood' with "+str(len(seash_global_variables.targets['downloadgood']))+" targets and 'downloadfail' with "+str(len(seash_global_variables.targets['downloadfail']))+" targets"




# download remotefn localfn
def download_filename_localfn(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  remotefn = command_key

  # Iterates through the dictionary to retrieve the user's argument input
  while input_dict[command_key]['name'] is not 'args':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  # handle '~'
  fileandpath = os.path.expanduser(command_key)
  localfn = fileandpath

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")



  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.download_target,localfn,remotefn)

  writestring = ''

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
      # for output...
      writestring = writestring + retdict[longname][1]+ " "
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if writestring:
    print "Wrote files: "+writestring

  # add groups if needed...
  if goodlist and faillist:
    seash_global_variables.targets['downloadgood'] = goodlist
    seash_global_variables.targets['downloadfail'] = faillist
    print "Added group 'downloadgood' with "+str(len(seash_global_variables.targets['downloadgood']))+" targets and 'downloadfail' with "+str(len(seash_global_variables.targets['downloadfail']))+" targets"
  
  



# delete remotefn             -- Delete a file
def delete_remotefn(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  remotefn = command_key

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")


  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.delete_target, remotefn)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else: 
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # add groups if needed...
  if goodlist and faillist:
    seash_global_variables.targets['deletegood'] = goodlist
    seash_global_variables.targets['deletefail'] = faillist
    print "Added group 'deletegood' with "+str(len(seash_global_variables.targets['deletegood']))+" targets and 'deletefail' with "+str(len(seash_global_variables.targets['deletefail']))+" targets"




# cat remotefn  -- Print a file to the screen
def cat_filename(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  remotefn = os.path.basename(command_key)

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")



  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.cat_target,remotefn)


  # here is where I list it out...
  for longname in retdict:

    # True means it worked
    if retdict[longname][0]:
      print
      print "File '"+remotefn+"' on '"+longname+"': "
      print retdict[longname][1]
      print
      goodlist.append(longname)

    else:
      print
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  if goodlist and faillist:
    seash_global_variables.targets['catgood'] = goodlist
    seash_global_variables.targets['catfail'] = faillist
    print "Added group 'catgood' with "+str(len(seash_global_variables.targets['catgood']))+" targets and 'catfail' with "+str(len(seash_global_variables.targets['catfail']))+" targets"




  
  

  
# start file [args ...]  -- Start an experiment
def start_remotefn(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the repy version to run
  while input_dict[command_key]['name'] is not 'start':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  command = command_key

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  argstring = ' '.join([command_key])

  prog_platform = seash_helper.get_execution_platform(command,
    command_key)

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  # need to get the status, etc (or do I just try to start them all?)
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(
    seash_global_variables.targets[environment_dict['currenttarget']],
    seash_helper.start_target, argstring, prog_platform)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # add groups if needed...
  if goodlist and faillist:
    seash_global_variables.targets['startgood'] = goodlist
    seash_global_variables.targets['startfail'] = faillist
    print "Added group 'startgood' with "+str(len(seash_global_variables.targets['startgood']))+" targets and 'startfail' with "+str(len(seash_global_variables.targets['startfail']))+" targets"





# start file arg
def start_remotefn_arg(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the repy version to run
  while input_dict[command_key]['name'] is not 'start':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  command = command_key

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  filename = command_key

  # Iterates through the dictionary to retrieve the user's argument input
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  arguments = command_key

  argstring = ' '.join([filename] + [arguments])

  prog_platform = seash_helper.get_execution_platform(command,
    filename)

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  # need to get the status, etc (or do I just try to start them all?)
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(
    seash_global_variables.targets[environment_dict['currenttarget']],
    seash_helper.start_target, argstring, prog_platform)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # add groups if needed...
  if goodlist and faillist:
    seash_global_variables.targets['startgood'] = goodlist
    seash_global_variables.targets['startfail'] = faillist
    print "Added group 'startgood' with "+str(len(seash_global_variables.targets['startgood']))+" targets and 'startfail' with "+str(len(seash_global_variables.targets['startfail']))+" targets"





# stop               -- Stop an experiment
def stop(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  # need to get the status, etc (or do I just try to stop them all?)
  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.stop_target)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)


  # add groups if needed...
  if goodlist and faillist:
    seash_global_variables.targets['stopgood'] = goodlist
    seash_global_variables.targets['stopfail'] = faillist
    print "Added group 'stopgood' with "+str(len(seash_global_variables.targets['stopgood']))+" targets and 'stopfail' with "+str(len(seash_global_variables.targets['stopfail']))+" targets"




# run file [args...]    -- Shortcut for upload a file and start
def run_localfn(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the repy version to run
  while input_dict[command_key]['name'] is not 'run':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  command = command_key

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
     input_dict = input_dict[command_key]['children']
     command_key = input_dict.keys()[0]

  # Handle '~' in file names
  fileandpath = os.path.expanduser(command_key)
  onlyfilename = os.path.basename(fileandpath)

  argstring = " ".join([onlyfilename])

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  prog_platform = seash_helper.get_execution_platform(command,
    onlyfilename)

  # read the local file...
  fileobj = open(fileandpath,"r")
  filedata = fileobj.read()
  fileobj.close()


  # to prevent timeouts during file uploads on slow connections, 
  # temporarily sets the timeout count on all vessels to be the  
  # time needed upload the file with the current globaluploadrate 
  seash_helper.set_upload_timeout(filedata) 


  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(
    seash_global_variables.targets[environment_dict['currenttarget']],
    seash_helper.run_target, onlyfilename, filedata, argstring,
    prog_platform)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['rungood'] = goodlist
    seash_global_variables.targets['runfail'] = faillist
    print "Added group 'rungood' with "+str(len(seash_global_variables.targets['rungood']))+" targets and 'runfail' with "+str(len(seash_global_variables.targets['runfail']))+" targets"


  # resets the timeout count on all vessels to globalseashtimeout 
  seash_helper.reset_vessel_timeout() 





# run file arg
def run_localfn_arg(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the repy version to run
  while input_dict[command_key]['name'] is not 'run':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  command = command_key

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  # Handle '~' in file names
  fileandpath = os.path.expanduser(command_key)
  onlyfilename = os.path.basename(fileandpath)

  # Iterates down one more level to retrieve the argument string
  input_dict = input_dict[command_key]['children']
  command_key = input_dict.keys()[0]

  argstring = " ".join([onlyfilename] + [command_key])

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  prog_platform = seash_helper.get_execution_platform(command,
    onlyfilename)

  # read the local file...
  fileobj = open(fileandpath,"r")
  filedata = fileobj.read()
  fileobj.close()


  # to prevent timeouts during file uploads on slow connections, 
  # temporarily sets the timeout count on all vessels to be the  
  # time needed upload the file with the current globaluploadrate 
  seash_helper.set_upload_timeout(filedata) 


  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(
    seash_global_variables.targets[environment_dict['currenttarget']],
    seash_helper.run_target, onlyfilename, filedata, argstring,
    prog_platform)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['rungood'] = goodlist
    seash_global_variables.targets['runfail'] = faillist
    print "Added group 'rungood' with "+str(len(seash_global_variables.targets['rungood']))+" targets and 'runfail' with "+str(len(seash_global_variables.targets['runfail']))+" targets"


  # resets the timeout count on all vessels to globalseashtimeout 
  seash_helper.reset_vessel_timeout() 




#split resourcefn            -- Split off of each vessel another vessel
def split_resourcefn(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's filename
  while input_dict[command_key]['name'] is not 'filename':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  # expand ~
  fileandpath = os.path.expanduser(command_key)
  resourcefn = fileandpath

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  resourcefo = open(resourcefn)
  resourcedata = resourcefo.read()
  resourcefo.close() 


  faillist = []
  goodlist1 = []
  goodlist2 = []

  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.split_target,resourcedata)

  for longname in retdict:
    if retdict[longname][0]:
      newname1, newname2 = retdict[longname][1]
      goodlist1.append(newname1)
      goodlist2.append(newname2)
      print longname+" -> ("+newname1+", "+newname2+")"
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist1 and goodlist2 and faillist:
    seash_global_variables.targets['split1'] = goodlist1
    seash_global_variables.targets['split2'] = goodlist2
    seash_global_variables.targets['splitfail'] = faillist
    print "Added group 'split1' with "+str(len(seash_global_variables.targets['split1']))+" targets, 'split2' with "+str(len(seash_global_variables.targets['split2']))+" targets and 'splitfail' with "+str(len(seash_global_variables.targets['splitfail']))+" targets"
  elif goodlist1 and goodlist2:
    seash_global_variables.targets['split1'] = goodlist1
    seash_global_variables.targets['split2'] = goodlist2
    print "Added group 'split1' with "+str(len(seash_global_variables.targets['split1']))+" targets and 'split2' with "+str(len(seash_global_variables.targets['split2']))+" targets"

  


#join                        -- Join vessels on the same node
def join(input_dict, environment_dict):

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  if not environment_dict['currentkeyname'] or not seash_global_variables.keys[environment_dict['currentkeyname']]['publickey'] or not seash_global_variables.keys[environment_dict['currentkeyname']]['privatekey']:
    raise seash_exceptions.UserError("Must specify an identity with public and private keys...")

  nodedict = {}
  skipstring = ''

  # Need to group vessels by node...
  for longname in seash_global_variables.targets[environment_dict['currenttarget']]:
    if seash_global_variables.keys[environment_dict['currentkeyname']]['publickey'] != seash_global_variables.vesselinfo[longname]['ownerkey']:
      skipstring = skipstring + longname+" "
      continue

    nodename = seash_global_variables.vesselinfo[longname]['IP']+":"+str(seash_global_variables.vesselinfo[longname]['port'])

    if nodename not in nodedict:
      nodedict[nodename] = []

    nodedict[nodename].append(longname)

  # if we skip nodes, explain why
  if skipstring:
    print "Skipping "+skipstring+" because the current identity is not the owner."
    print "If you are trying to join vessels with different owners, you need"
    print "to change ownership to the same owner first"


  faillist = []
  goodlist = []

  retdict = seash_helper.contact_targets(nodedict.keys(),seash_helper.join_target,nodedict)

  for nodename in retdict:

    if retdict[nodename][0]:
      print retdict[nodename][1][0],"<- ("+", ".join(nodedict[nodename])+")"
      goodlist = goodlist + nodedict[nodename]
    else:
      if retdict[nodename][1]:
        faillist = faillist + nodedict[nodename]
      # Nodes that I only have one vessel on don't get added to a list...
  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['joingood'] = goodlist
    seash_global_variables.targets['joinfail'] = faillist
    print "Added group 'joingood' with "+str(len(seash_global_variables.targets['joingood']))+" targets and 'joinfail' with "+str(len(seash_global_variables.targets['joinfail']))+" targets"
  elif goodlist:
    seash_global_variables.targets['joingood'] = goodlist
    seash_global_variables.targets['joinfail'] = faillist
    print "Added group 'joingood' with "+str(len(seash_global_variables.targets['joingood']))+" targets"




###Set Commands###

# set                 -- Changes the state of the targets (use 'help set')
def set(input_dict, environment_dict):
  pass
        




# set owner identity        -- Change a vessel's owner
def set_owner_arg(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  newowner = command_key

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  if newowner not in seash_global_variables.keys:
    raise seash_exceptions.UserError("Unknown identity: '"+newowner+"'")

  if not seash_global_variables.keys[newowner]['publickey']:
    raise seash_exceptions.UserError("No public key for '"+newowner+"'")

  faillist = []
  goodlist = []
  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.setowner_target,newowner)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)


  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['ownergood'] = goodlist
    seash_global_variables.targets['ownerfail'] = faillist
    print "Added group 'ownergood' with "+str(len(seash_global_variables.targets['ownergood']))+" targets and 'ownerfail' with "+str(len(seash_global_variables.targets['ownerfail']))+" targets"
  




# set autosave [ on | off ] -- Set whether SeaSH automatically saves the last state.
def set_autosave_arg(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  if command_key == 'on':
    environment_dict['autosave'] = True
  elif command_key == 'off':
    environment_dict['autosave'] = False
  else:
    raise seash_exceptions.UserError("Usage: set autosave [ on | off (default)]")





# set advertise [ on | off ] -- Change advertisement of vessels
def set_advertise_arg(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  if command_key == 'on':
    newadvert = True
  elif command_key == 'off':
    newadvert = False
  else:
    raise seash_exceptions.UserError("Usage: set advertise [ on | off ]")

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")


  faillist = []
  goodlist = []
  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.setadvertise_target,newadvert)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['advertisegood'] = goodlist
    seash_global_variables.targets['advertisefail'] = faillist
    print "Added group 'advertisegood' with "+str(len(seash_global_variables.targets['advertisegood']))+" targets and 'advertisefail' with "+str(len(seash_global_variables.targets['advertisefail']))+" targets"
  
    

  

# set ownerinfo [ data ... ]    -- Change owner information for the vessels
def set_ownerinfo_arg(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  newdata = command_key

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")

  faillist = []
  goodlist = []
  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.setownerinformation_target,newdata)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)
  seash_helper.print_vessel_errors(retdict)


  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['ownerinfogood'] = goodlist
    seash_global_variables.targets['ownerinfofail'] = faillist
    print "Added group 'ownerinfogood' with "+str(len(seash_global_variables.targets['ownerinfogood']))+" targets and 'ownerinfofail' with "+str(len(seash_global_variables.targets['ownerinfofail']))+" targets"


  

# set users [ identity ... ]  -- Change a vessel's users
def set_users_arg(input_dict, environment_dict):
  userkeys = []

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  userlist = command_key.split()

  for identity in userlist:
    if identity not in seash_global_variables.keys:
      raise seash_exceptions.UserError("Unknown identity: '"+identity+"'")

    if not seash_global_variables.keys[identity]['publickey']:
      raise seash_exceptions.UserError("No public key for '"+identity+"'")

    userkeys.append(rsa.rsa_publickey_to_string(seash_global_variables.keys[identity]['publickey']))
  # this is the format the NM expects...
  userkeystring = '|'.join(userkeys)

  if not environment_dict['currenttarget']:
    raise seash_exceptions.UserError("Must specify a target")


  faillist = []
  goodlist = []
  retdict = seash_helper.contact_targets(seash_global_variables.targets[environment_dict['currenttarget']],seash_helper.setusers_target,userkeystring)

  for longname in retdict:
    if retdict[longname][0]:
      goodlist.append(longname)
    else:
      faillist.append(longname)

  seash_helper.print_vessel_errors(retdict)

  # update the groups
  if goodlist and faillist:
    seash_global_variables.targets['usersgood'] = goodlist
    seash_global_variables.targets['usersfail'] = faillist
    print "Added group 'usersgood' with "+str(len(seash_global_variables.targets['usersgood']))+" targets and 'usersfail' with "+str(len(seash_global_variables.targets['usersfail']))+" targets"
  
    


# set timeout count  -- Sets the time that seash is willing to wait on a node
def set_timeout_arg(input_dict, environment_dict):

  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  # I need to set the timeout for new handles...
  try:
    seash_global_variables.globalseashtimeout = int(command_key)
  except ValueError:
    raise seash_exceptions.UserError("The timeout value must be a number")

  # let's reset the timeout for existing handles...
  for longname in seash_global_variables.vesselinfo:
    thisvesselhandle = seash_global_variables.vesselinfo[longname]['handle']
    thisvesselhandledict = nmclient.nmclient_get_handle_info(thisvesselhandle)
    thisvesselhandledict['timeout'] = seash_global_variables.globalseashtimeout
    nmclient.nmclient_set_handle_info(thisvesselhandle,thisvesselhandledict)


          
# set uploadrate speed     -- Sets the speed seash will modify the timeout count with when uploading files
def set_uploadrate_arg(input_dict, environment_dict):

  try:
    command_key = input_dict.keys()[0]

    # Iterates through the dictionary to retrieve the user's argument
    while input_dict[command_key]['name'] is not 'args':
      input_dict = input_dict[command_key]['children']
      command_key = input_dict.keys()[0]

    seash_global_variables.globaluploadrate = int(command_key)
  except ValueError:
    raise seash_exceptions.UserError("The speed value must be a number (in bytes per second)")


# set showparse [on | off] -- Toggles display of the parsed commandline input
def set_showparse_args(input_dict, environment_dict):
  command_key = input_dict.keys()[0]

  # Iterates through the dictionary to retrieve the user's argument
  while input_dict[command_key]['name'] is not 'args':
    input_dict = input_dict[command_key]['children']
    command_key = input_dict.keys()[0]

  command_key = command_key.lower()
  if command_key == 'on':
    environment_dict['showparse'] = True
  elif command_key == 'off':
    environment_dict['showparse'] = False
  else:
    raise seash_exceptions.UserError("Value can be either 'on' or 'off'") 


# enable modulename
def enable_module(input_dict, environment_dict):
  # Enables an installed module.

  # Get the modulename
  dict_mark = input_dict
  try:
    command = dict_mark.keys()[0]
    while dict_mark[command]['name'] != 'modulename':
      dict_mark = input_dict[command]['children']
      command = dict_mark.keys()[0]
    modulename = command
  except IndexError:
    raise seash_exceptions.UserError("Error, command requires a modulename")

  try:
    seash_modules.enable(seash_dictionary.seashcommanddict, modulename)
  except seash_exceptions.ModuleConflictError, e:
    print "Module cannot be imported due to the following conflicting command:"
    print str(e)


# disable modulename
def disable_module(input_dict, environment_dict):
  # Disables an enabled module.

  # Get the modulename
  dict_mark = input_dict
  try:
    command = dict_mark.keys()[0]
    while dict_mark[command]['name'] != 'modulename':
      dict_mark = input_dict[command]['children']
      command = dict_mark.keys()[0]
    modulename = command
  except IndexError:
    raise seash_exceptions.UserError("Error, command requires a modulename")

  seash_modules.disable(seash_dictionary.seashcommanddict, modulename)

# modulehelp modulename
def print_module_help(input_dict, environment_dict):
  # Prints the helptext for a module

  # Get the modulename
  dict_mark = input_dict
  try:
    command = dict_mark.keys()[0]
    while dict_mark[command]['name'] != 'modulename':
      dict_mark = input_dict[command]['children']
      command = dict_mark.keys()[0]
    modulename = command
  except IndexError:
    raise seash_exceptions.UserError("Error, command requires a modulename")

  # Is this module installed?
  if not modulename in seash_modules.module_data:
    raise seash_exceptions.UserError("Module is not installed.")

  print seash_modules.module_data[modulename]['help_text']

  # Now, print out all the commands under this module
  print "Commands in this module:"
  print '\n'.join(seash_helper.get_commands_from_commanddict(seash_modules.module_data[modulename]['command_dict']))
  


# show modules
def list_all_modules(input_dict, environment_dict):
  # Lists all modules and their status.
  print "Enabled Modules:"
  print ", ".join(seash_modules.get_enabled_modules())
  print
  print "Installed Modules:"

  # Now print the URLs...
  # Output format:
  # modulename - URL not available  # URL is set to None
  # modulename - https://seattle.poly.edu/seashplugins/modulename/ # URL is set
  for module in seash_modules.module_data:
    print module, '-',
    if seash_modules.module_data[module]['url'] is None:
      print "Install URL not available"
    else:
      print seash_modules.module_data[module]['url']
  print



# exit
def exit(input_dict, environment_dict):
  sys.exit()
