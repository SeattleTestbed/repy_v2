"""
<Program>
  initialize.py 
  
<Started>
  August 2014.

<Authors>
  Albert Rafetseder
  Chintan Choksi
  
<Purpose>
  This script does a "git clone" of all the dependent repositories
  of a Seattle component.

<Usage>
  * Clone the repository you would like to build on your machine, e.g. using 
      "git clone https://github.com/SeattleTestbed/seash"
  
  * Change into the "scripts" subdirectory
  
  * Run this script: "python initialize.py [-s]"
  
  * The dependencies will be checked out into "../DEPENDENCIES"
  
  *"initialize.py" will get the list of dependencies to check-out from
    "config_initialize.txt" file.
  
  * During check-out, if there is a readme file associated with a repository,
    then it will be printed on terminal.  Once this is done, run the build.py
    script to import the necessary files into a desired target folder.  Run
    build file as: "python build.py"

  The "-s" command-line option is optional, and activates skip mode.  Skip
  mode is useful to

  (1) Save you from re-downloading stuff that you have on your local machine
  (and can copy over via "cp -R" or similar).
  
  (2) Test local modifications that you have in your working copy without
  having to first commit them somewhere and then hack the init config, but
  
  Skip mode does not check whether the repos that exist in "DEPENDENCIES/" are
  complete, in a working state, or are on the branch specified in
  "config_initialize.txt".  Consequently, while skip mode sounds like a good
  thing to have if you want to pick up the initialization process again after
  interrupting it, it is also pretty dangerous (as in: weird build/runtime
  problems) and should be used with extreme care.

<Note>
  While this file is redistributed with every buildable Seattle repo, 
  the "master copy" (and thus the most up-to-date version) is kept 
  at: https://github.com/SeattleTestbed/buildscripts
"""

import subprocess
import os
import sys


# config_initialize.txt contains links to repository and the directory where it
# gets checked-out.
# E.g.: https://github.com/SeattleTestbed/seash ../DEPENDENCIES/seash
config_file = open("config_initialize.txt")

if len(sys.argv) == 2 and sys.argv[1] == '-s':
  ignore_git_errors = True
else:
  ignore_git_errors = False

for line in config_file.readlines():
  # Ignore comments and blank lines
  if line.startswith("#") or line.strip() == '':
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
    if not ignore_git_errors:
      print """Since the skip-mode is off, these errors need to be fixed before the build process can proceed. In 
doubt, please contact the Seattle development team at 

   seattle-devel@googlegroups.com

and supply all of the above information. Thank you!

"""
      print
      sys.exit(1)
    else:
      print "Continuing with the cloning of directories as skip-mode is active"
      print
      continue

# If there is a readme file, show it to the user. 
try:
  readme_file = open('README.txt', 'r')
  for line in readme_file.readlines():
    print line
  readme_file.close()
except IOError:
  # There is no readme file, or we can't access it.
  pass

