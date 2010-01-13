# Test flush...   I guess I just see if it throws an exception?
fo = file("junk_test.out",'w')
fo.flush()
fo.write("foo")
fo.flush()
fo.close()

fo = file("junk_test.out",'r')
data = fo.read()
fo.close()
print "foo"==data
