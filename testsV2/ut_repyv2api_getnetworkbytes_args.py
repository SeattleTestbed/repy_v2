# This tests all sorts of bad arguments to ensure they are caught

#pragma repy


for bad_arg in ["abc", 123, None, ""]:
  try:
    get_network_bytes(bad_arg )
  except RepyArgumentError:
  # expected
    pass
  else:
    log("Bad argment " + str(bad_arg) + " allowed for interface",'\n')
