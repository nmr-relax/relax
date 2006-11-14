#!/usr/bin/env python
import os,re,unittest,string,sys

def getStartupPath():
  startupPath = sys.path[0]
  if startupPath == '':
      startupPath = sys.getcwd()
  return startupPath

def getModuleRelativePath(modulePath,rootPaths=None):
    ''' find the relative path of a module (?package) to one
        of a set of root paths

        @type  filePath: string
        @param filePath: path of a python module

        @type  rootPaths: sequence of strings
        @param rootPaths: a set of paths to search for the module in.if None is
               passed the list is initialized from the internal PYTHONPATH
               sys.path. Elements which are empty strings are replace with
               the cureent working directory sys.getcwd()

        @returns: a relative module path to one of the rootPaths which is
                  sepparated by '.' if the modulePath is a subpath of one of
                  the root paths otherwise None

        '''

    relativePath  = None
    if rootPaths == None:
        rootPaths = sys.path
    for rootPath in rootPaths:
        rootPath =segmentPath(os.path.abspath(rootPath))
        modulePath = segmentPath(os.path.abspath(modulePath))

        commonPrefix = getCommonPrefix(rootPath,modulePath)
        if commonPrefix == rootPath:
            relativePath = modulePath[len(commonPrefix):]
            break

    if relativePath !=  None:
        relativePath = '.'.join(relativePath)

    return relativePath



def getCommonPrefix(path1,path2):
    resultPath = []
    for elem1,elem2 in map(None,path1,path2):
        if elem1 == None or elem2 == None:
            break

        if elem1 == elem2:
          resultPath.append(elem1)
    return resultPath

def segmentPath(path,normalise=True):
    if normalise:
        path = os.path.normpath(path)
    result  =  []
    (head,tail) = os.path.split(path)

    while head != '' and tail != '':
        result.append(tail)
        head,tail = os.path.split(head)
    result.reverse()
    return result


class TestFinder:
    pattern = re.compile('test_.*\.py$')
    suite = unittest.TestSuite()
    def __init__(self,rootPath=None):
        self.rootPath = rootPath
        if self.rootPath == None:
            self.rootPath = getStartupPath()

#    def importClass(self,name):
#        mod = __import__(name)
#        components = name.split('.')
#        for comp in components[1:]:
#            mod = getattr(mod, comp)
#        return mod

#    def commonPrefix(self,path1,path2):
#        resultPath = []
#        for elem1,elem2 in map(None,path1,path2):
#            if elem1 == None or elem2 == None:
#                break
#
#            if elem1 == elem2:
#              resultPath.append(elem1)
#        return resultPath



    def scanPaths(self,rootPath):
        #rootPathSegments = segmentPath(self.rootPath)
        #print 'root path:',rootPathSegments

        for (dirpath, dirnames, filenames) in os.walk(rootPath):
             #print dirpath, dirnames, filenames
             for filename in filenames:
                 if self.pattern.match(filename):

                     filename = os.path.splitext(filename)[0]
                     relativeModulePath  =  getModuleRelativePath(dirpath)
                     #print filename, type(string.upper(filename[0])), type(filename[1])
                     className = string.upper(filename[0]) + filename[1:]
                     print relativeModulePath, className, filename
                     if relativeModulePath != '':
                         modulePath = '.'.join((relativeModulePath,filename))
                     else:
                         modulePath = filename
                     print modulePath,className
                     module  = __import__ (modulePath)
                     clazz =  getattr(module,className)


                     self.suite = unittest.TestLoader().loadTestsFromTestCase(clazz)
    #
    def run(self):
        runner = unittest.TextTestRunner()
        runner.run(self.suite)

class run_unit_tests(object):
    ''' class to run  a particular unit test or a directory of unit tests'''

    def __init__(self, rootPath=None, testModule=None,
                 testPattern = ['test_(\.*).py'],
                 rootSystemDirectory = 'test_suite/..',
                 rootUnitTestDirectory = 'unit_tests'):
        ''' initialise the unit test runner

          @type  rootPath: a string containing a directory name
          @param rootPath: root path to start searching for modules to unit test
                 from ususally this is the current working directory.

          @type  testModule: string
          @param testModule: the name of a module to unit test. If the variable
                 is None it will default to the current working directorys
                 contents. Otherwise it will be used as a module path from the
                 current working directory.

          @type  testPattern: a list of strings containing patterns
          @param testPattern: a list of patterns against which files will be
                 tested to see if they are expected to contain unit tests. If
                 the file has the correct pattern the class
                 <fileName>.<capitalisedFileName> will be searched for
                 testCases e.g in the case of test_float.py the combination
                 would be test_float.Test_float.

          @type  rootSystemDirectory: a string containing a directory name
          @param rootSystemDirectory: the directory from which the distribution
                 is rooted. This is viewed as the the 'PYTHONPATH'
                 of the classes to be tested. It must be unique and defined
                 relative to the test suite. For the current setup
                 in relax this is 'test_suite/..'.

          @type  rootUnitTestDirectory: a string containing a directory name
          @param rootUnitTestDirectory: the directory from which all unit
                 module directories descend. For the current setup in relax
                 this is 'unit_tests'.
        '''

        self.testModule = testModule
        if self.testModule == None:
            self.testModule = sys.getcwd()

        self.testPattern = testPattern
        self.rootSystemDirectory = rootSystemDirectory
        self.rootUnitTestDirectory = rootUnitTestDirectory

    # should this be get last...
    def getFirstInstancePath(self,path,targetDirectory):
        ''' get the minimal path searching down the file system to
            targetDirectory Note the algorithm understands .. and .

            @type path:  a directory path in a string
            @param path: a directory path so search down

            @type  targetDirectory: a directory  name in a string
            @param targetDirectory: a directory to find in the path

        '''
        segPath = segmentPath(os.path.abspath(path))
        foundPath = None
        stack = []
        for seg in segPath():
            if seg == '..':
                stack.pop()
            elif seg == '.':
                continue
            else:
                stack.push(seg)

            if stack[-1] == targetDirectory:
                foundPath = os.path.join(segPath[:i+1])
                break

        return foundPath

    def findUnitTestDirectoryPath(self,path):
        ''' find the path to the unit_test directory starting from path and
            using self.rootUnitTestDirectory

             @type  path: a string containing a directory path
             @param path: a path to a point to start searching to the system
                    directory from.
        '''

        return getFirstInstancePath(path,self.rootUnitTestDirectory)


    def findSystemDirectoryPath(self,path):
        ''' find the path to the relax system starting from path and using
            self.rootSystemDirectory

             @type  path: a string containing a directory path
             @param path: a path to a point to start searching to the system
                    directory from.
        '''
        return getFirstInstancePath(path,self.rootSystemDirectory)



    def pathFromTestModule(self,rootPath):
       ''' determine the path of the self.testModule starting from rootPath

           currently this assumes that if the last two names in testModule are
           the same barring an initial  capital letter in the class name
           then we can just look for the module. Thus the class name is popped
           off and we then join the moduleName together with the root unit test
           path and a '.py'

           note we can't deal with module methods...

           @type  rootPath: string containing a directory name
           @param rootPath: directory to start looking for the module from
        '''

        unitTestDirectory  = findUnitTestDirectoryPath(rootPath)
        testModuleSegs = split(self.testModule,'.')


        result = None
        if len(testModuleSegs) >= 2:
            putativeClassName =  testModuleSegs[-1]
            classFromModuleName = string.lower(putativeClassName[0])+ putativeClassName[:1]
            putativeModuleName = testModuleSegs[-2]





            if classFromModuleName == putativeModuleName:
                copyTestModuleSegs =  copy(testModuleSegs)
                copyTestModuleSegs.pop()
                classFileName = copyTestModuleSegs.pop()
                classFileName = classFileName + '.py'
                testPath = os.path.join(unitTestDirectory,copyTestModuleSegs, classFileName)


                if os.path.isfile(testPath):
                    result = testPath

         if result == None:
             result  = os.path.join(unitTestDirectory,testModuleSegs)

         return result




    def runTests(self):
        systemDirectory = self.findSystemDirectoryPath(self.rootPath)
        unitTestDirectory = self.findUnitTestDirectoryPath(self.rootPath)
        modulePath = self.pathFromTestModule(self,self.rootPath)

        # add UnitTestDirectory to python path
        #iterate and load unit tests from module path
        # add SystemDirectory to python path
        # iterate and load files to be tested

if __name__ == '__main__':
    print '1',getModuleRelativePath('/A/B/C',('/A/B',))
    print '2',getModuleRelativePath('/A/B/C',('/A/B/C',))
    print '3',getModuleRelativePath('/A/B/C',('/A/B/D/W',))
    print getCommonPrefix(('A','B','C'),('A','B','C'))
    print getCommonPrefix(('A','B','C'),('A','B','C','D'))
    print getCommonPrefix(('D','E'),('A','B','C','D'))
    print getCommonPrefix(('A','B','C','F'),('A','B','C','D'))
    print getCommonPrefix((),('A','B','C','D'))
    print ('A','B','C') == ('A','B','C')
    finder = TestFinder()
    finder.scanPaths()
    finder.run()
# todo normcase home