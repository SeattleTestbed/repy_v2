# I've moved it to undefined because I don't know how to set up the server side
# of this test in a good way...
if callfunc == 'initialize':


  settimer(2, exitall,())
  try:
    # To unit test this, I need to know a host that won't let me complete the 
    # openconn.   How do I get this?
    sockobj = openconn("128.208.3.202",12345,timeout=1)
  except:
    pass
  else:
    sockobj.close()

  print "next"


