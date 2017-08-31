"""
This unit test checks that listfiles consumes 4K of fileread.
"""

#pragma repy

files = listfiles()

lim, usage, stops = getresources()

if usage["fileread"] != 4096:
  log("File read should be 4096! Resources: "+str(usage),'\n')


