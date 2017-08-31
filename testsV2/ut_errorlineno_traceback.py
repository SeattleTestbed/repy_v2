#pragma repy
#pragma error line 40
#pragma error line 31
#pragma error line 38
"""The traceback should look like this:
Uncaught exception!
---
Following is a full traceback, and a user traceback.
The user traceback excludes non-user modules. The most recent call is displayed last.

Full debugging traceback:
  "repy.py", line 154, in execute_namespace_until_completion
  "/Users/justincappos/seattle/repy_v2/RUNNABLE/virtual_namespace.py", line 124, in evaluate
  "/Users/justincappos/seattle/repy_v2/RUNNABLE/safe.py", line 591, in safe_run
  "RepyV2:ut_errorlineno_traceback.py", line 40, in <module>
  "RepyV2:ut_errorlineno_traceback.py", line 31, in foo
  "RepyV2:ut_errorlineno_traceback.py", line 38, in bar

User traceback:
  "RepyV2:ut_errorlineno_traceback.py", line 40, in <module>
  "RepyV2:ut_errorlineno_traceback.py", line 31, in foo
  "RepyV2:ut_errorlineno_traceback.py", line 38, in bar

Exception (with type 'exceptions.TypeError'): unsupported operand type(s) for +: 'int' and 'str'
---

"""
# Check that the traceback's line numbers are also adjusted...

def foo():
  bar()  # 31st line


def bar():
  a = 3
  b = 's'
  # type error on the next line
  c = a + b    # 38th line

foo()   # This is the 40th line
