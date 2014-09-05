#This is a wrapper script that automates the execution of build_component.py and facilitates the user by avoiding 
#changing of directories manually.

import os
import subprocess

common_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),"../DEPENDENCIES/common/build_component.py" )
execfile(common_dir)
