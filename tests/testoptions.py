# This simply produces some output on stdout and stderr so we can test if
# logfiles work with parameters in different orders.

if callfunc=='initialize':
  print "hi"
  print 1/0
