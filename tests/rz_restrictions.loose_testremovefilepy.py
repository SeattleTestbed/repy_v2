# create a junk.py file
myfo = open("junk.py","w")
print >> myfo, "print 'Hello world'"
myfo.close()

removefile("junk.py")   # should be removed...
