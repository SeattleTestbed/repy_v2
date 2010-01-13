fo = file("junk_test.out",'w')
fo.write("foo")
fo.close()
fo = file("junk_test.out",'r')
data = fo.read()
fo.close()
print "foo"==data
