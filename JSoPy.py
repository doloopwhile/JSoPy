#!python2
# -*- coding: ascii -*-
from __future__ import print_function
from PyV8 import JSClass, JSContext

PrimitiveClasses = (str, int)

class WrappedPythonObject(JSClass):
    def __init__(self, py_obj):
        self._py_obj = py_obj
    
    def __str__(self):
        return "[object WrappedPythonObject({})]".format(repr(self._py_obj))
    
    def __getattr__(self, name):
        sub_obj = getattr(self._py_obj, name)
        if isinstance(sub_obj, PrimitiveClasses):
            return sub_obj
        else:
            return WrappedPythonObject(sub_obj)
    
    
class Python(JSClass):
    def print(self, x):
        print(x)
    
    def _import(self, module_path):
        module = __import__(module_path)
        return WrappedPythonObject(module)
    
    def __getattr__(self, name):
        if name == "import":
            return self._import
        else:
            return JSClass.__getattr__(self, name)
    
    
class Global(JSClass):
    def __init__(self):
        self.py = Python()
    
    @property
    def window(self):
        return self

def main():
    import sys
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-c", "--command", type=str)
    parser.add_argument("script", nargs="?", type=str)
    
    opts = parser.parse_args()
    
    if not (opts.command or opts.script):
        parser.print_usage()
        sys.exit(1)
    
    if opts.command:
        js = opts.command
    else:
        with io.open(opts.script) as fp:
            js = fp.read()
    
    global_ = Global()
    with JSContext(global_) as ctx:
        ctx.eval(js)
    
if __name__ == "__main__":
    main()
    