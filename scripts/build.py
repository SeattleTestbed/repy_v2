"""
<Program>
  build.py

<Purpose>
  This is a wrapper script for SeattleTestbed/common/build_component.py. 
  It makes it so that users can start build_component without changing 
  directories.
  build_component, in turn, makes runnable Seattle components out of 
  source repositories.

<Usage>
  python build.py [TARGET_DIR]

  TARGET_DIR is an optional target directory for the build process. 
      When omitted, /path/to/component/RUNNABLE is used instead.

<Note>
  While this file is redistributed with every buildable Seattle repo, 
  the ``master copy'' (and thus the most up-to-date version) is kept 
  at https://github.com/SeattleTestbed/buildscripts
"""

import os
import sys

# Add build_component.py's path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../DEPENDENCIES/common/"))

import build_component
build_component.main()

