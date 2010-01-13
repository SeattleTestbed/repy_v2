fo = file("junk_test.out",'w')
settimer(.5,exitall,())
fo.write("fooalsdfjlasdlfjajsdfkjaskjdfk") # write won't complete
print "Never gets here"
