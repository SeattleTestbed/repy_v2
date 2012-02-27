from safe import *

# A bunch of unit tests to run if this file is ran directly.
if __name__ == '__main__':
    import unittest
    
    class TestSafe(unittest.TestCase):
        def test_check_node_import(self):
            self.assertRaises(exception_hierarchy.CheckNodeException,safe_exec,"import os")
        def test_check_node_from(self):
            self.assertRaises(exception_hierarchy.CheckNodeException,safe_exec,"from os import *")
        def test_check_node_exec(self):
            self.assertRaises(exception_hierarchy.CheckNodeException,safe_exec,"exec 'None'")
        def test_check_node_raise(self):
            self.assertRaises(exception_hierarchy.CheckNodeException,safe_exec,"raise Exception")
        def test_check_node_global(self):
            self.assertRaises(exception_hierarchy.CheckNodeException,safe_exec,"global abs")
        
        def test_check_str_x(self):
            self.assertRaises(exception_hierarchy.CheckStrException,safe_exec,"x__ = 1")
        def test_check_str_str(self):
            self.assertRaises(exception_hierarchy.CheckStrException,safe_exec,"x = '__'")
        def test_check_str_class(self):
            self.assertRaises(exception_hierarchy.CheckStrException,safe_exec,"None.__class__")
        def test_check_str_func_globals(self):
            self.assertRaises(exception_hierarchy.CheckStrException,safe_exec,"def x(): pass; x.func_globals")
        def test_check_str_init(self):
            safe_exec("def __init__(self): pass")
        def test_check_str_subclasses(self):
            self.assertRaises(exception_hierarchy.CheckStrException,safe_exec,"object.__subclasses__")
        def test_check_str_properties(self):
            code = """
class X(object):
    def __get__(self,k,t=None):
        1/0
"""
            self.assertRaises(exception_hierarchy.CheckStrException,safe_exec,code)
        def test_check_str_unicode(self):
            self.assertRaises(exception_hierarchy.CheckStrException,safe_exec,"u'__'")
        
        def test_run_builtin_open(self):
            self.assertRaises(exception_hierarchy.RunBuiltinException,safe_exec,"open('test.txt','w')")
        def test_run_builtin_getattr(self):
            self.assertRaises(exception_hierarchy.RunBuiltinException,safe_exec,"getattr(None,'x')")
        def test_run_builtin_abs(self):
            safe_exec("abs(-1)")
        def test_run_builtin_open_fnc(self):
            def test():
                f = open('test.txt','w')
            self.assertRaises(exception_hierarchy.RunBuiltinException,safe_exec,"test()",{'test':test})
        def test_run_builtin_open_context(self):
            #this demonstrates how python jumps into some mystical
            #restricted mode at this point .. causing this to throw
            #an IOError.  a bit strange, if you ask me.
            self.assertRaises(IOError,safe_exec,"test('test.txt','w')",{'test':open})
        def test_run_builtin_type_context(self):
            #however, even though this is also a very dangerous function
            #python's mystical restricted mode doesn't throw anything.
            safe_exec("test(1)",{'test':type})
        def test_run_builtin_dir(self):
            self.assertRaises(exception_hierarchy.RunBuiltinException,safe_exec,"dir(None)")
        
        def test_run_exeception_div(self):
            self.assertRaises(ZeroDivisionError,safe_exec,"1/0")
        def test_run_exeception_i(self):
            self.assertRaises(ValueError,safe_exec,"(-1)**0.5")
        
        def test_misc_callback(self):
            self.value = None
            def test(): self.value = 1
            safe_exec("test()", {'test':test})
            self.assertEqual(self.value, 1)
        def test_misc_safe(self):
            self.value = None
            def test(v): self.value = v
            code = """
class Test:
    def __init__(self,value):
        self.x = value
        self.y = 4
    def run(self):
        for n in xrange(0,34):
            self.x += n
            self.y *= n
        return self.x+self.y
b = Test(value)
r = b.run()
test(r)
"""
            safe_exec(code,{'value':3,'test':test})
            self.assertEqual(self.value, 564)
            
        def test_misc_context_reset(self):
            #test that local contact is reset
            safe_exec("abs = None")
            safe_exec("abs(-1)")
            safe_run("abs = None")
            safe_run("abs(-1)")
            
        def test_misc_syntax_error(self):
            self.assertRaises(SyntaxError,safe_exec,"/")
            
        def test_misc_context_switch(self):
            self.value = None
            def test(v): self.value = v
            safe_exec("""
def test2():
    open('test.txt','w')
test(test2)
""",{'test':test})
            self.assertRaises(exception_hierarchy.RunBuiltinException,safe_exec,"test()",{'test':self.value})
        
        def test_misc_context_junk(self):
            #test that stuff isn't being added into *my* context
            #except what i want in it..
            c = {}
            safe_exec("b=1",c)
            self.assertEqual(c['b'],1)
            
        def test_misc_context_later(self):
            #honestly, i'd rec that people don't do this, but
            #at least we've got it covered ...
            c = {}
            safe_exec("def test(): open('test.txt','w')",c)
            self.assertRaises(exception_hierarchy.RunBuiltinException,c['test'])
        
        #def test_misc_test(self):
            #code = "".join(open('test.py').readlines())
            #safe_check(code)
            
        def test_misc_builtin_globals_write(self):
            #check that a user can't modify the special _builtin_globals stuff
            safe_exec("abs = None")
            self.assertNotEqual(_builtin_globals['abs'],None)
            
        #def test_misc_builtin_globals_used(self):
            ##check that the same builtin globals are always used
            #c1,c2 = {},{}
            #safe_exec("def test(): pass",c1)
            #safe_exec("def test(): pass",c2)
            #self.assertEqual(c1['test'].func_globals,c2['test'].func_globals)
            #self.assertEqual(c1['test'].func_globals,_builtin_globals)
        
        def test_misc_builtin_globals_used(self):
            #check that the same builtin globals are always used
            c = {}
            safe_exec("def test1(): pass",c)
            safe_exec("def test2(): pass",c)
            self.assertEqual(c['test1'].func_globals,c['test2'].func_globals)
            self.assertEqual(c['test1'].func_globals['__builtins__'],_builtin_globals)
            self.assertEqual(c['__builtins__'],_builtin_globals)
            
        def test_misc_type_escape(self):
            #tests that 'type' isn't allowed anymore
            #with type defined, you could create magical classes like this: 
            code = """
def delmethod(self): 1/0
foo=type('Foo', (object,), {'_' + '_del_' + '_':delmethod})()
foo.error
"""
            try:
                self.assertRaises(exception_hierarchy.RunBuiltinException,safe_exec,code)
            finally:
                pass
            
        def test_misc_recursive_fnc(self):
            code = "def test():test()\ntest()"
            self.assertRaises(RuntimeError,safe_exec,code)
            

    unittest.main()

    #safe_exec('print locals()')
