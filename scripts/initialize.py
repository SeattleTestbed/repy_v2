"""
<Program>
  initialize.py 
  
<Date Started>
  July 5th, 2014

<Author>
  Chintan Choksi

<Purpose>
  This script does a git check-out of all the dependent repositories 
  to the current directory.
  
<Usage>
  * Clone the repository you would like to build on your machine, e.g. using 
      ``git clone https://github.com/SeattleTestbed/seash''
  * Change into the ``scripts'' subdirectory
  * Run this script: 
      ``python initialize.py''
  * The dependencies will be checked out into the current directory.
   
"""

import subprocess
import os
import sys


config_file = open("config_initialize.txt")

for line in config_file.readlines():
  # Ignore comments and blank lines
  if line.startswith("#") or line.strip == '':
    continue

  # If we end up here, the line contains a Git URL (+options?) for us to clone
  print "Checking out repo from", line.split()[0], "..."
  git_process = subprocess.Popen("git clone " + line, cwd = os.getcwd(), shell = True, 
     stdout = subprocess.PIPE, stderr = subprocess.PIPE )
  (stdout_data, stderr_data) = git_process.communicate()

  # Git prints all status messages to stderr (!). We check its retval 
  # to see if it performed correctly, and halt the program (giving debug 
  # output) if not.
  if git_process.returncode == 0:
     print "Done!"
  else:
    print "*** Error checking out repo. Git returned status code", git_process.returncode
    print "*** Git messages on stdout: '" + stdout_data + "'."
    print "*** Git messages on stderr: '" + stderr_data + "'."
    print
    print """These errors need to be fixed before the build process can proceed. In 
doubt, please contact the Seattle development team at 

   seattle-devel@googlegroups.com

and supply all of the above information. Thank you!

"""
    sys.exit(1)


# If there is a readme file, show it to the user. 
try:
  readme_file = open('README.txt', 'r')
  for line in readme_file.readlines():
    print line
  readme_file.close()
except IOError:
  # There is no readme file, or we can't access it.
  pass

