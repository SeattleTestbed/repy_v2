# We just write a bit of data to disk indefinately. 
# When the resource parent is killed, we should die.

if callfunc == "initialize":
  fileo = open("junk_test.out", "w")
  
  while True:
    fileo.write("Still Running!")
    fileo.flush()
    sleep(0.1)

