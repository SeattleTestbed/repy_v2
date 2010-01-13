if callfunc == "initialize":
  def foo():
    a = openconn("127.0.0.1", <connport>)

  def bar(a,b,c,d,e):
    mycontext["count"] += 1
    if mycontext["count"] >= 6:
      stopcomm(e)
    

  mycontext["count"] = 0
  waitforconn("127.0.0.1", <connport>, bar)

  foo()
  foo()
  foo()
  foo()
  foo()
  foo()
