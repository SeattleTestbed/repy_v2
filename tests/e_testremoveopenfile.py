
fro = open("junk_test.out","w")

removefile("junk_test.out") # can't remove an open file. Should be an exception
