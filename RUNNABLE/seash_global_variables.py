"""
Author: Alan Loh
Module: Holds and keeps track of the global variables that contains
        information in regards to the current session seash.

Holds any global variables that's not already in environment_dict and
needs to be accessed by multiple files.
"""

# a dict that contains all of the targets (vessels and groups) we know about.
targets = {'%all':[]}

# stores information about the vessels...
vesselinfo = {}

# the nextid that should be used for a new target.
nextid = 1

# a dict that contains all of the key information
keys = {}

# With the addition of affixes, affixes slow down openconnection a lot
# with their lookups and will trigger numerous timeouts.  Make sure
# there's enough time to account for the affixes overhead, at least
# until that is fixed.

# this is how long we wait for a node to timeout
globalseashtimeout = 30

# this is the upload rate we'll modify globalseashtimeout during 
# file uploads to ensure completion without timeout
# default is left at 10240 bytes/sec (10 kb/sec)
globaluploadrate = 5120
