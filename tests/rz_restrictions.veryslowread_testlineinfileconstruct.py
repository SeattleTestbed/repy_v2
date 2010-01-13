fo = file("hello.multiline",'rb')
settimer(.5,exitall,())

time_start = getruntime()
for line in fo:
  pass
time_end = getruntime()

# We won't finish reading all the lines in time because the file's too big
# and the read rate is very slow.

print "Never going to see this!"
print "Reading the whole file took %f seconds." % (time_end - time_start)
