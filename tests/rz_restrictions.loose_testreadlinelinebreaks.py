fobj = open("junk.out", "w+")
fobj.write("line 1\r\nline 2\n")
fobj.flush()
fobj.seek(0)

line1 = fobj.readline()
line2 = fobj.readline()

try:
  assert line1.endswith("\n")
  assert line2.endswith("\n")
  assert fobj.readline() == ""

finally:
  fobj.close()
  removefile("junk.out")
