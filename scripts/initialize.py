
"""
# !/usr/bin/python

<Program>
  initialize.py 
  
<Date Started>
  July 5th, 2014

<Author>
  Chintan Choksi

<Purpose>
  This script does a git check-out of all the dependent repositories to the home directory.
  
<Usage>
  How to run this program:
  1. Clone the dist repository to local machine, and run this script
  2. To Run this script: 
  dist user$ python initialize.py
   
"""


import commands
import subprocess
import os
import sys


alist = [line.rstrip('\n') for line in open('config_initialize.txt')]
length = len(alist)

count =0
while(count < length):
  repo=alist[count]
  alist0=repo.split(' ', 1)[0]
  #print alist0
  if alist0 != "test" and alist0 != "install" and alist0 != "#":
    pr = subprocess.Popen("git clone https://github.com/SeattleTestbed/"+ alist[count] , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    (out, error) = pr.communicate()
    count =count+1
    print str("Checking out repo")
    print count
  elif alist0 == "install":
    repo=alist[count]
    alist1=repo.split(' ', 1)[1]
    count=count+1
    pr = subprocess.Popen("pip install git+https://github.com/SeattleTestbed/"+ alist1 , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    pr = subprocess.Popen("git clone https://github.com/SeattleTestbed/"+ alist1 , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    print str("Checking out repo")
    print count
  elif alist0 == "test":
    repo=alist[count]
    alist1=repo.split(' ', 1)[1]
    count=count+1
    pr = subprocess.Popen("pip install git+git://github.com/SeattleTestbed/"+ alist1 , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    pr = subprocess.Popen("git clone https://github.com/SeattleTestbed/"+ alist1 , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    print str("Checking out repo")
    print count
  





