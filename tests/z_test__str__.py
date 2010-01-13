
class foo():
  def __str__(self):
    return "hello"

if str(foo()) != "hello":
  print "str(foo()) should have been 'hello', not", str(foo())
