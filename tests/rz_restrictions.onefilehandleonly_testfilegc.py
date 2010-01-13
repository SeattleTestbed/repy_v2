if callfunc == "initialize":
  a = file("junk_test.out2", "wb")
  a.write("awdafawd")
  a.close()

  for line in file("junk_test.out2"):
    pass

  for line in file("junk_test.out2"):
    pass

  for line in file("junk_test.out2"):
    pass

  for line in file("junk_test.out2"):
    pass

  a = file("junk_test.out2", "wb")
  a.close()

  for line in file("junk_test.out2"):
    pass

  for line in file("junk_test.out2"):
    pass
