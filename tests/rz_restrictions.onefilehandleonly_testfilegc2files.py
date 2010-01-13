# Test file GC, with two different files.

if callfunc == "initialize":
  # Create files to make sure they exist.
  a = file("junk_test.out", "w")
  a.write("awdawdf")
  a.close()
  a = file("junk_test.out2", "w")
  a.write("awdawdf")
  a.close()

  for line in file("junk_test.out"):
    pass

  for line in file("junk_test.out2"):
    pass

  for line in file("junk_test.out"):
    pass

  for line in file("junk_test.out2"):
    pass

  for line in file("junk_test.out"):
    pass

  for line in file("junk_test.out2"):
    pass
