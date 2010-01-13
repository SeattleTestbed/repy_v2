if callfunc == "initialize":
  # first, initialize by creating the file we'll read.
  fobj = open("junk_test.out", 'w')
  fobj.write("hello")
  fobj.close()
  
  # now the actual test
  max_len = 3
  fobj = open("junk_test.out", 'rb')
  lines = fobj.readlines(max_len)

  total_len = 0
  last_len = 0

  for line in lines:
    linelen = len(line)
    total_len += linelen
    last_len = linelen

  if total_len - last_len > max_len:
    print "This shouldn't happen!"
