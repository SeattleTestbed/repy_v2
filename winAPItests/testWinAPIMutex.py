# Import the API
import windows_api

# So that we can sleep
import time

# Shortcut to avoid typing
win = windows_api

# Default lock name
lockname = "Global\\SEA"

# Period to retain lock (seconds)
WAIT_INTERVAL = 2

# Time to acquire mutex (milliseconds)
ATTEMPT_MAX = 500

# Num of times to hold
HOLD_TIMES = 3

# Num of times held
held = 0

# Create a mutex
handle = win.createMutex(lockname)
print "Handle: " + str(handle) # Print handle id out
print "Create: " + str(win._getLastError()) # Print the error number on creation

while True:
  # Try to acquire lock
  lock = win.acquireMutex(handle, ATTEMPT_MAX)
  if lock: held += 1
  print "Locked: " + str(lock)

  if held == HOLD_TIMES: # Release the lock if we hit the limit
    print "Releasing..."
    win.releaseMutex(handle)
    held = 0

  time.sleep(WAIT_INTERVAL)