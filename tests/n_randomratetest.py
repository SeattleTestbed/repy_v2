def foo():
  exitall()

settimer(5, foo, ())

for num in range(50):
  randomfloat()
# generate lots of numbers.   With rate limiting, the timer should fire first...
print "This should be reached when there aren't time restrictions"
