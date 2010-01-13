fo = file("hello")
data1 = fo.readline()
fo.seek(0)
data2 = fo.readline()
print data1==data2
