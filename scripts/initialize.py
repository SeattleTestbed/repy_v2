
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


lines = [line.rstrip('\n') for line in open('config_initialize.txt')]
alist = list(line for line in lines if line)
length = len(alist)

count =0
while(count < length):
  repo=alist[count]
  alist0=repo.split(' ', 1)[0]
  #print alist0
  if alist0 != "test" and alist0 != "install" and alist0 != "#":
    pr = subprocess.Popen("git clone "+ alist[count] , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    (out, error) = pr.communicate()
    print str("Checking out repo:")
    print alist[count]
    count =count+1
  elif alist0 == "install":
    repo=alist[count]
    alist1=repo.split(' ', 1)[1]
    pr = subprocess.Popen("pip install "+ alist1 , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    pr = subprocess.Popen("git clone "+ alist1 , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    print str("Checking out repo:")
    print alist1
    count=count+1
  elif alist0 == "test":
    repo=alist[count]
    alist1=repo.split(' ', 1)[1]
    pr = subprocess.Popen("git clone "+ alist1 , cwd = os.getcwd(), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
    print str("Checking out repo")
    print alist1
    count=count+1
  





