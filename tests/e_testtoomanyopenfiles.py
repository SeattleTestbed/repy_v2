if callfunc == 'initialize':
  hi = open("hello","r")
  hi1 = open("hello1","r")
  hi2 = open("hello2","r")
  hi3 = open("hello3","r")
  hi4 = open("hello4","r")
  hi5 = open("hello5","r") # should be an exception (too many open files)
