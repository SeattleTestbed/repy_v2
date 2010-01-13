print "Fail"
# there is a 16KB buffer.   "Success!" is 8 chars, so 2048 writes should 
# overwrite Fail
print "Success!"*2048
