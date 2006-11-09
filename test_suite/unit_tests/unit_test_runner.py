#!/usr/bin/env python
import os,re,unittest,string,sys

class TestFinder:
    pattern = re.compile('test.*\.py$')
    suite = unittest.TestSuite()
    def __init__(self,rootPath=None):
        self.rootPath = rootPath
        if self.rootPath == None:
            self.rootPath = os.getcwd()
    def importClass(self,name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod     
    
    def scanPaths(self,path=None):
        for (dirpath, dirnames, filenames) in os.walk(self.rootPath):
             print dirpath, dirnames, filenames
             for filename in filenames:
                 if self.pattern.match(filename):
                     moduleName  = os.path.splitext(filename)[0]
                     className = string.upper(moduleName[0]) + moduleName[1:]
                     module  = __import__ (moduleName)
                     clazz =  getattr(module,className)
                     
                     
                     self.suite = unittest.TestLoader().loadTestsFromTestCase(clazz)
    #             
    def run(self):
        runner = unittest.TextTestRunner()
        runner.run(self.suite)
        
class run_unit_tests(object):
    def __init__(self,test_directory=None):
        pass
if __name__ == '__main__':
    finder = TestFinder()
    finder.scanPaths()
    finder.run()
