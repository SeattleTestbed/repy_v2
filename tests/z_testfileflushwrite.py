if callfunc == "initialize":
  filename = "junk_test.out"
  mode = "w+b"
  num = "2"
  fobj = open(filename,mode)
  try:
    fobj.write(num)
    fobj.flush()

    fobj.seek(0)
    if fobj.read(1) != num:
        print ' write did not flush to disk on mode: '+mode
  finally:
    fobj.close()
