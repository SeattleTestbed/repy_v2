class myerror(Exception):
  pass

try:
  raise myerror, "Error"
except myerror:
  pass
