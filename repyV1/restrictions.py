"""
   Author: Justin Cappos

   Start Date: 27 June 2008

   Description:

   This class handles access control for functions, objects, etc.
   Many of the functions here are intentionally written in a braindead way.
   This module is supposed to be readable and obviously correct.   I could have
   used the re module, etc. and made this much cleverer than it needs to be.
"""



# this does the resource tracking / process stopping
import nanny

# Used to handle internal errors
import tracebackrepy

""" 
The restrictions file format consists of lines that look like this:
 
Comment Lines: 
# This is a comment


Resource restrictions: what the program is allowed to utilize
Usage: resource resourcename limit
Example:
resource CPU 0.1			# Can have %10 CPU utilization
resource memory 33554432		# Can have 32 MB of memory
resource outsockets 1			# Can initiate one outgoing comm
resource insocket 2			# Can listen for 2 incoming comms
resource messport_2023 			# Can use messageport 2023 


Call restrictions: perform some action when a call occurs
Usage: call callname [arg restrictions] [allow / deny / prompt]	
restrictions are of the form: [[arg num is string | noargs is num ] ... ]
Example:
call exitall allow   			# always allow exitall calls
call sleep arg 0 is 0.1 allow 		# allow sleep calls of len 0.1 second
call open arg 1 is r allow   		# allow read of any file in their dir
call open arg 0 is foo arg 1 is w allow	# allow write if it is to foo
call open arg 1 is w deny		# deny any other writes
call file.write noargs is 2 deny	# deny any call to write with 2 args




Notes:
Lines are parsed in order and the first rule that applies to a call is used.
For example:

call open arg 1 is foo allow
call open arg 2 is w deny

These rules will allow 'foo' to be opened for writing.

Any unmatched call is automatically denied.   

Wildcards may not be used.

There is no support for the 'or' operation.

Floating point numbers and integers must match their string representation!!!
I.e. 0.1 not .1 and 2 not 02.

"""



class ParseError(Exception):
  pass









valid_actions = [ "allow", "deny", "prompt" ]

known_calls = [ "canceltimer", "exitall", "file.close", "file.flush",
	"file.__init__", "file.next", "file.read", "file.readline",
	"file.readlines", "file.seek", "file.write", "file.writelines",
	"listdir", "removefile", "gethostbyname_ex", "getmyip", "open", 
	"openconn", "recvmess", "sendmess", "settimer", "sleep",
	"socket.close", "socket.recv", "socket.send", "stopcomm", 
	"waitforconn", "log.write", "log.writelines", "randomfloat", 
	"getruntime", "getlock","get_thread_name","VirtualNamespace"
	]



# Each rule can either be matched or not.   Matched rules apply to the call

# this table is indexed by call name and contains tuples of (rule, action)
call_rule_table = {}




############################## Parsing ###############################

# given a list of tokens, produce a rule
def get_rule(rulelist):

  if len(rulelist) == 0:
    return []

  # I'm going to walk through the current list and consume tokens as I build 
  # the rule
  currentlist = rulelist

  myrule = []

  while currentlist != []:

    if currentlist[0] == 'arg':

      # it's of the format: arg num is val

      # must have at least 4 args
      if len(currentlist)<4:
        raise ParseError, "Not enough tokens for 'arg'"

      # second arg must be an integer value
      try:
        int(currentlist[1])
      except ValueError:
        raise ParseError, "invalid argument number '"+currentlist[1]+"'"
      
      # third arg must be 'is'
      if currentlist[2] != 'is':
        raise ParseError, "arg missing 'is' keyword, instead found '"+currentlist[2]+"'"

      # add this to the rule...
      myrule.append(('arg',int(currentlist[1]),currentlist[3]))

      # remove these tokens from the currentlist
      currentlist = currentlist[4:]
     
      continue
      
    elif currentlist[0] == 'noargs':

      # it's of the format: noargs is val

      # must have at least 3 args
      if len(currentlist)<3:
        raise ParseError, "Not enough tokens for 'noargs'"

      
      # second arg must be 'is'
      if currentlist[1] != 'is':
        raise ParseError, "arg missing 'is' keyword, instead found '"+currentlist[1]+"'"

      # third arg must be an integer value
      try:
        int(currentlist[2])
      except ValueError:
        raise ParseError, "invalid argument number '"+currentlist[2]+"'"


      # add this to the rule...
      myrule.append(('noargs',int(currentlist[2])))

      # remove these tokens from the currentlist
      currentlist = currentlist[3:]
     
      continue
  
    else:
      raise ParseError, "invalid rule type '"+currentlist[0]+"'"
  

  return myrule



# This is a braindead parser.   It's supposed to be readable and obviously 
# correct, not "clever"
def init_restriction_tables(filename):

  # create an empty rule for each call
  for callname in known_calls:
    call_rule_table[callname] = []



  for line in open(filename):
    # remove any comments
    noncommentline = line.split('#')[0]

    # the items are all separated by spaces
    tokenlist = noncommentline.split()

    if len(tokenlist) == 0:
      # This was a blank or comment line
      continue
 
    # should be either a resource or a call line
    if tokenlist[0] != 'resource' and tokenlist[0] != 'call':
      raise ParseError, "Line '"+line+"' not understood in file '"+filename+"'"
    


    if tokenlist[0] == 'resource':

      ####### Okay, it's a resource.  It must have two other tokens!
      if len(tokenlist) != 3:
        raise ParseError, "Line '"+line+"' has wrong number of items in '"+filename+"'"
      # and the second token must be a known resource
      if tokenlist[1] not in nanny.known_resources:
        raise ParseError, "Line '"+line+"' has an unknown resource '"+tokenlist[1]+"' in '"+filename+"'"

      # and the last item should be a valid float
      try:
        float(tokenlist[2])
      except ValueError:
        raise ParseError, "Line '"+line+"' has an invalid resource value '"+tokenlist[2]+"' in '"+filename+"'"

      # if it's an individual_item_resource, we'll handle it here...
      if tokenlist[1] in nanny.individual_item_resources:
        nanny.resource_restriction_table[tokenlist[1]].add(float(tokenlist[2]))
        continue

      # if normal that resource should not have been previously assigned
      if tokenlist[1] in nanny.resource_restriction_table:
        raise ParseError, "Line '"+line+"' has a duplicate resource rule for '"+tokenlist[1]+"' in '"+filename+"'"

        
      # Finally, we assign it to the table
      nanny.resource_restriction_table[tokenlist[1]] = float(tokenlist[2])
      
      # Let's do the next line!
      continue




    elif tokenlist[0] == 'call':

      ################# it was a call...

      # The second token should be a valid call name
      if tokenlist[1] not in known_calls:
        raise ParseError, "Line '"+line+"' has an unknown call '"+tokenlist[1]+"' in '"+filename+"'"
      
      # The last token should be a valid action
      if tokenlist[-1] not in valid_actions:
        raise ParseError, "Line '"+line+"' has an unknown action '"+tokenlist[-1]+"' in '"+filename+"'"

      # Get the rule for this action
      try:
        rule = get_rule(tokenlist[2:-1])
      except ValueError, e:
        raise ParseError, "Line '"+line+"' has error '"+str(e)+"' in '"+filename+"'"
        
      # append a tuple containing the rule and action
      call_rule_table[tokenlist[1]].append((rule, tokenlist[-1]))


      # Let's do the next line!
      continue

    else:
      raise ParseError, "Internal error for '"+line+"' in file '"+filename+"'"


  # make sure that if there are required resources, they are defined
  for resource in nanny.must_assign_resources:
    if resource not in nanny.resource_restriction_table:
      raise ParseError, "Missing required resource '"+resource+"' in file '"+filename+"'"


  # give any remaining resources an entry with 0.0 as the value

  for resource in nanny.known_resources:
    if resource not in nanny.resource_restriction_table:
      nanny.resource_restriction_table[resource] = 0.0







######################### Rule Parsing ##############################


# a rulelist looks like [ ('arg',2,'foo'), ('noargs',1), ... ]
def match_rule(rulelist, args):
  # always match the empty rule
  if rulelist == []:
    return (True, '', 'Always match the empty rule')

  # go through the rules.   If we fail to match one then return False
  for rule in rulelist:

    # rule type is an 'arg':   'arg', pos, 'value'
    if rule[0] == 'arg':

      if len(args) <= rule[1]:
        # Can't be a match, we don't have this arg
        return (False, rule, 'Missing arg')
 
      if str(args[rule[1]]) != rule[2]:
        # Doesn't match the value specified
        return (False, rule, 'Value not allowed')

    # rule type is an 'noargs':   'noargs', count
    elif rule[0] == 'noargs':

      if len(args) != rule[1]:
        # Wrong number of args
        return (False, rule, 'Wrong args count')

  # we must not have failed any rule...
  return (True, '', 'All rules satisfied')





# rulesets look like: [ ([('arg',2,'foo'),('noargs',1)],'allow'), ([],'deny') ]
# I'm going to write this recursively
def find_action(ruleset, args):
  # There wasn't a matching rule so deny
  if ruleset == []:
    return [('deny', '', 'No matching rule found')]

  # this should be a tuple of two arguments, a rule and an action
  thisrule, thisaction = ruleset[0]
  match = match_rule(thisrule, args)
  matched, matched_rule, reasoning = match
  if matched:
    return [(thisaction, matched_rule, reasoning)]

  # do the recursive bit...
  return find_action(ruleset[1:], args)+[match]









####################### Externally called bits ############################


# allow restrictions to be disabled to fix #919
disablerestrictions = False


def assertisallowed(call,*args):
  if disablerestrictions:
    return True

  # let's pre-reject certain open / file calls
  #print call_rule_table[call]
  matches = find_action(call_rule_table[call], args)
  action, matched_rule, reasoning = matches[0]
  if action == 'allow':
    return True
  elif action == 'deny':
    matches.reverse()
    estr = "Call '"+str(call)+"' with args "+str(args)+" not allowed\n"
    estr += "Matching dump:\n"
    for action, matched_rule, reasoning in matches:
      if matched_rule != '':
        estr += "rule: "+str(matched_rule) + ", "
      estr += str(reasoning) + "\n"
    raise Exception, estr
  elif action == 'prompt':
    # would do an upcall here...
    raise Exception, "Call '"+ str(call)+"' not allowed"
  else:
    # This will cause the program to exit and log things if logging is
    # enabled. -Brent
    tracebackrepy.handle_internalerror("find_action returned '" + str(action) +
        "' for call '" + str(call) + "'", 31)



def init_restrictions(filename):
  # Set up tables that list the rules and resource restrictions
  init_restriction_tables(filename)

  # This flushes and initializes the tables that track resource consumption
  nanny.initialize_consumed_resource_tables()

  # Start the nanny to check resource use...
  nanny.start_resource_nanny()

