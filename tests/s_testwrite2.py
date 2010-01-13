fo = file("junk_test.out",'w')
print >> fo, "foo"
fo.close()
fo = file("junk_test.out",'r')
data = fo.read()
fo.close()
print "foo"==data.strip()
