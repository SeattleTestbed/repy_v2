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

config_file = open("config_initialize.txt")

for line in config_file.readlines():
  # Ignore comments and blank lines
  if line.startswith("#") or line=='\n':
    continue

  # If we end up here, the line contains a Git URL (+options?) for us to clone
  print "Checking out repo from", line.split()[0], "..."
  pr = subprocess.Popen("git clone " + line, cwd = os.getcwd(), shell = True, 
     stdout = subprocess.PIPE, stderr = subprocess.PIPE )
  (out, error) = pr.communicate()
  print "Done!"

