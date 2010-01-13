def foo(num):
  print "Hahaha",num

setattr(sys, 'exit', foo)
