"""
This unit test checks the listfiles API call.

We check:
  1) That z_testlistfiles.py is listed
  2) That repy.py is listed
  3) There are more that 50 files
"""

#pragma repy

# Get the list of files
files = set(listfiles())

if "ut_repyv2api_listfilesbasictest.py" not in files:
  log("This unit test is not in the list of files!",'\n')

if "repy.py" not in files:
  log("repy.py is not in the list of files!",'\n')

if len(files) < 50:
  log("There are less than 50 files!",'\n')


