# Conrad: contains the exception classes used by safe.py. Needed so that
# tracebackrepy.py can look out for safety exceptions without importing all
# of safe.py.

class SafeException(Exception):
    """Base class for Safe Exceptions"""
    def __init__(self,*value):
        self.value = str(value)
    def __str__(self):
        return self.value

class CheckNodeException(SafeException):
    """AST Node class is not in the whitelist."""
    pass

class CheckStrException(SafeException):
    """A string in the AST looks insecure."""
    pass

class RunBuiltinException(SafeException):
    """During the run a non-whitelisted builtin was called."""
    pass
