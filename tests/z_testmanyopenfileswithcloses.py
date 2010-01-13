
if callfunc == 'initialize':
  hi = open("hello","r")
  hi1 = open("hello1","r")
  hi.close()

  hi2 = open("hello2","r")
  hi3 = open("hello3","r")
  hi4 = open("hello4","r")
  hi1.close()
  hi5 = open("hello5","r")
  hi = open("hello","r")  # should be okay because it would total 5...
