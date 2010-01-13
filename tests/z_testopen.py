# Some tests to ensure open() behaves like our definition.

SEEK_SET = 0    # Absolute
SEEK_CUR = 1    # Relative
SEEK_END = 2    # End of the file

try:
  # Test basic writing / reading
  fro = open("junk_test.out", "w+")
  fro.write("hi!")
  fro.flush()
  fro.seek(0, SEEK_SET)
  contents = fro.read()
  fro.close()
  if contents != "hi!":
    print "Failed to write to / read from file!"

  fro = open("junk_test.out", "r")
  contents = fro.read()
  fro.close()
  if contents != "hi!":
    print "Failed to write to / read from file!"

  # Test "w" semantics
  fro = open("junk_test.out", "w+")
  contents = fro.read()
  if contents != "":
    print "Write mode fails to truncate file!"
  fro.seek(0, SEEK_SET)
  fro.write("Testing 123")
  fro.close()

  # Test append
  fro = open("junk_test.out", "a+")
  fro.write("abc")
  fro.flush()
  fro.seek(0, SEEK_SET)
  contents = fro.read()
  fro.close()
  if contents != "Testing 123abc":
    print "Append mode fails to append!"

finally:
  if "junk_test.out" in listdir():
    removefile("junk_test.out")
