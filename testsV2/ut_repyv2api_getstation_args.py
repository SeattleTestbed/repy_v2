# This tests all sorts of bad arguments to ensure they are caught

#pragma repy

for bad_arg in ["abc", 123, None, '']:
  try:
    get_station(bad_arg)
  except RepyArgumentError:
  # expected
    pass
  else:
    log("Bad argment " + bad_arg + " allowed for interface",'\n')