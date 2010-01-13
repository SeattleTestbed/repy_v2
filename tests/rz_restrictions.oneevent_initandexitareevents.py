# a test to see if the event used by the initialize thread is counted

# One thread for this code
if callfunc == 'initialize':
  # One event is fine
  pass

if callfunc == 'exit':
  # Exit code should be ok, because exit and initialize don't run at the
  # same time
  pass
