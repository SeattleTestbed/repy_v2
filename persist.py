""" 
Author: Justin Cappos
Module: Module for persisting data (one writer, one reader).   I will persist 
        data in a safe way where I can be interrupted at any point and will be 
        able to get the information back.

Start date: Sept 1st, 2008
The design goals of this version are to be secure, simple, and reliable 
(in that order).   

Were it not for the eval / repr ugliness, I would write this in repy...
"""

# NOTE: This is intended to be safe for one reader, one writer regardless of 
# when and where failures occur.   I assume this will break if there are 
# multiple of either.

# BUG: How do I ensure the file is flushed to disk?   Does flush / close do it?


# the commit protocol is:
# 1) if filename does not exist and filename+'.new' exists, move 
#    filename+'.new' to filename
# 2) open filename+'.new'
# 3) write the object
# 4) close the file 
# 5) delete filename
# 6) move filename+'.new' to filename
# 
# the reason for step 1 is in case a previous incarnation died after step 5
# but before step 6.
# the reason for having step 5 is (from the Python docs on os.rename): On 
# Windows, if dst already exists, OSError will be raised even if it is a file; 
# there may be no way to implement an atomic rename when dst names an existing 
# file.
#
# the recovery protocol is:
# 1) try to get the ctime for filename+'.new" 
# 2) try to copy filename to filename+".tmp" 
# 3) if step 2 succeeded, goto step 8
# 4) if step 1 failed, goto step 1
# 5) try to copy filename+'.new' to filename+'.tmp'
# 6) if step 5 failed, goto step 1
# 7) if the ctime of filename+'.new' != the ctime we saw in step 1 goto step 1
# 8) read the contents of filename+'.tmp'
# 9) delete filename+'.tmp'
# 10) return the result read in step 8
#
# The gist of what this does is: read filename if it exists.   If not, then
# readefilename+'.new' only if it doesn't change since the last time we checked
# for the existance of filename.
#
# This is complex because I need to prevent against race conditions.   The 
# problem is that it's hard to differentiate between another process that is
# doing a commit while I'm doing the recovery protocol and another process that
# died while doing the recovery protocol.   The specific case where this is a
# problem is when filename does not exist but filename+'.new' does.   A simple
# way to do recovery would be:
# 1) if filename exists, open it and return the contents
# 2) elif filename.'.new' exists, open it and return the contents
# 3) else throw an exception...
# the problem is that it may be that the other process had just completed step
# 4 of the commit protocol when we did step 1 and then may be on step 1 of the
# commit protocol when we do step 2.   We would get an empty file!
# To protect against this, I will copy the file I'm using to a temporary file
# and check the ctime of the file I use to ensure that it hasn't changed since
# I checked.  

# various file information / removal / renaming routines
import os

# copy
import shutil

# AR: Determine whether we're running on Android
try:
  import android
  is_android = True
except ImportError:
  is_android = False


def _copy(orig_filename, copy_filename):
  # AR: Wrap Android-specific shutil.copy() quirks. They seem to have a problem 
  # setting the file access mode bits there, and shutil.copyfile() suffices 
  # for the task at hand.

  if not is_android:
    shutil.copy(orig_filename, copy_filename)
  else:
    shutil.copyfile(orig_filename, copy_filename)



# commits the given object to a file with the provided name
def commit_object(object, filename):
  # the commit protocol is:

  # 1) if filename does not exist and filename+'.new' exists, move 
  #    filename+'.new' to filename
  if not os.path.exists(filename) and os.path.exists(filename+'.new'):
    os.rename(filename+'.new',filename)

  # 2) open filename+'.new'
  outobj = open(filename+'.new', "w")

  # 3) write the object
  outobj.write(repr(object))

  # 4) close the file 
  outobj.flush()
  outobj.close()

  # 5) delete filename
  # it should exist unless this is our first time...
  if os.path.exists(filename):
    os.remove(filename)
 
  # 6) move filename+'.new' to filename
  os.rename(filename+'.new',filename)
  

  

# reads the disk version of an object from a file with the provided name
def restore_object(filename):

  # BUG FIX:   Previously I just did os.listdir('.') below.   This makes 
  # this function fail if the file isn't in this directory.

  # I need to find the directory of the object.   
  filedirectory = os.path.dirname(filename)

  # I need to find the filename of the object.   
  filenameonly = os.path.basename(filename)

  # however, for some silly reason, this sometimes returns '' instead of '.'
  if filedirectory == '':
    filedirectory = '.'

  # I'm assuming that listdir is an atomic way that I'll be able to check for
  # the existence of filename and filename.new

  # either filename or filename+'.new' must exist (or else something is wrong)
  filelist = os.listdir(filedirectory)
  
  if filenameonly not in filelist and filenameonly+'.new' not in filelist:
    raise ValueError, "Filename '"+filename+"' missing."

  # the recovery protocol is:
  while True:
    # 1) try to get the ctime for filename+'.new" 
    try:
      currentctime = os.path.getctime(filename+'.new')
    except OSError, e:
      if e[0] == 2: # file not found
        currentctime = None
      else:
        raise
    
    # 2) try to copy filename to filename+".tmp" 
    try:
      _copy(filename, filename+'.tmp')
    except IOError, e:
      if e[0] == 2: # file not found
        pass
      else:
        raise
    else:
      # 3) if step 2 succeeded, goto step 8
      break
    
    # 4) if step 1 failed, goto step 1
    if currentctime == None:
      continue

    # 5) try to copy filename+'.new' to filename+'.tmp'
    try:
      _copy(filename+'.new', filename+'.tmp')
    except IOError, e:
      if e[0] == 2: # file not found
        # 6) if step 5 failed, goto step 1
        continue
      else:
        raise

    # 7) if the ctime of filename+'.new' != the ctime we saw in step 1 then 
    #    goto step 1
    try:
      latestctime = os.path.getctime(filename+'.new')
    except OSError, e:
      if e[0] == 2: # file not found
        continue
      else:
        raise

    if latestctime != currentctime:
      continue


  # 8) read the contents of filename+'.tmp'
  readfileobj = open(filename+'.tmp')
  readdata = readfileobj.read()
  readfileobj.close()

  # 9) delete filename+'.tmp'
  os.remove(filename+'.tmp')

  # 10) return the result read in step 8
  return eval(readdata)
