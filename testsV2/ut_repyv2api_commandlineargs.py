"""
Verify that the Repy sandbox parses command-line arguments correctly.
For example,
  python repy.py restrictionsfile my_program.r2py --logfile ABCDEF

must *not* result in the sandbox consuming the ``--logfile'' arg and 
writing the vessel log to the named file. Instead, the sandboxed 
program should see the arg.

We test this by calling repy.py with arguments similar to the above, 
and a no-op (empty) RepyV2 program. 
If repy.py creates the named logfile, this is an error. If the file is 
not created, we take this to mean that the sandboxed program gets the 
argument (although we don't check this specifically).

Note: This test overwrites / removes files from the current working dir. 
The chosen `program_name` and `logfile_prefix` should be unlikely to 
clash with anything you created, but you have been warned.
"""

import sys
import os
import portable_popen
import time


# Create an empty RepyV2 program. Remove any previous file of this name first.
program_name = "noop_program_for_repy_callarg_test.r2py"
try:
  os.remove(program_name)
except OSError:
  # The file wasn't there. No problem.
  pass

noop_prog = open(program_name, "w")
noop_prog.close()


# Call Repy. If repy.py mistakingly consumes the --logfile arg, it 
# will create a file named logfile_prefix + ".old" (or .new if .old 
# already existed).
logfile_prefix = "REPY_CALLARG_TEST"
repy_process = portable_popen.Popen([sys.executable, "repy.py", 
    "restrictions.default", program_name, "--logfile", logfile_prefix])

# Give things time to settle (launching of subprocess, code safety check, etc.)
time.sleep(5)

# See if the logfile was created. 
for filename in os.listdir("."):
  if filename.startswith(logfile_prefix):
    print "Found file", filename, "which indicates that repy.py consumed "
    print "the argument meant for the sandboxed program. Bad."
    break


# Finally, remove any files we might created
for filename in [program_name, logfile_prefix+".old", logfile_prefix+".new"]:
  try:
    os.remove(filename)
  except OSError:
    pass

