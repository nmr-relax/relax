#!/usr/bin/env python
################################################################################
#                                                                              #
# Copyright (C) 2006  Gary S Thompson (see https://gna.org/users/varioustoxins #
#                                      for contact details)                    #
#                                                                              #
#                                                                              #
# This file is part of the program relax.                                      #
#                                                                              #
# relax is free software; you can redistribute it and/or modify                #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation; either version 2 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# relax is distributed in the hope that it will be useful,                     #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with relax; if not, write to the Free Software                         #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA    #
#                                                                              #
################################################################################

''' unit_test_runner provides utilities for the running of unit tests from the
    command line or within the relax testing frame work.

    Unit tests in the relax frame work are stored in a directory structure
    rooted at <relax-root-directory>/test_suite/unit_tests. The directory
    unit tests contains a directory structure that mirrors the relax directory
    structure and which ideally contains one unit test file/module for each
    file/module in the relax framework. The default convention is that the unit
    test module for a relax module called <relax-module> is called
    test_<relax-module> (stored in test_<relax-module>.py). The unit test module
    test_<relax-module> should then contain a class called Test_<relax-module>
    which is a child of TestCase and contains methods whose names start with
    'test' and take no arguments other than self.

    A concrete example:

    for class <relax-root-directory>/maths-fns/chi2.py ***complete***




    The framework can discover sets of unit tests from the file system and add
    them to TestSuites either from the command line or programmatically from
    inside another program. It also has the ability to search for a  root unit
    test and system directory from a position anywhere inside the unit test
    hierarchy.

    TODO: examine PEP 338 and runpy.run_module(modulename): Executing Modules as Scripts
          for a later version of relax that is dependant on python 2.5
'''

import os,re,unittest,string,sys
from optparse import OptionParser
from textwrap import dedent

#import Tkinter as tk
#import unittest.unittestgui as unitgui

# constants
###########
PY_FILE_EXTENSION='py'

# utility functions
###################


def get_startup_path():
    '''Get the path of the directory the program started from.

       The startup path is the first path in sys.path (the internal PYTHONPATH)
       by convention. If the first element of sys.path is an empty trying the
       current working directory is used instead.
    '''

    startup_path = sys.path[0]
    if startup_path == '':
        startup_path = os.getcwd()
    return startup_path

def import_module(module_path):

    module = __import__(module_path)
    result = [module]
    components = module_path.split('.')
    for component in components[1:]:
        module = getattr(module, component)
        result.append(module)
    return result


def get_module_relative_path(module_path, root_paths=None):
    '''Find the relative path of a module to one of a set of root paths.

       As the module may match moregetStartupPath than one path the first path that
       can contain it is chosen.

       @type  module_path: string
       @param module_path: path of a python module


       @type  root_paths: sequence of strings
       @param root_paths: a set of paths to search for the module in.if None is
              passed the list is initialized from the internal PYTHONPATH
              sys.path. Elements which are empty strings are replace with
              the current working directory sys.getcwd()


       @returns: a relative module path to one of the rootPaths which is
                 separated by '.'s if the modulePath is a subpath of one of
                 the root paths, otherwise None

    '''

    relative_path = None
    if root_paths == None:
        root_paths = sys.path
    for root_path in root_paths:
        root_path = segment_path(os.path.abspath(root_path))
        module_path = segment_path(os.path.abspath(module_path))

        common_prefix = get_common_prefix(root_path, module_path)
        if common_prefix == root_path:
            relative_path = module_path[len(common_prefix):]
            break

    if relative_path != None:
        relative_path = '.'.join(relative_path)

    return relative_path


def get_common_prefix(path1, path2):
    '''Get the common prefix between two paths.

       @type path1: a list of path segments
       @param path1: the first path to be compared

       @type path2: a list of path segments
       @param path2: the second path to be compared

       @return: the common path shared between the two paths starting from the
                root directory as a list of segments. If there is no common
                path an empty list is returned.
    '''

    result_path = []
    for elem1,elem2 in map(None, path1, path2):
        if elem1 == None or elem2 == None:
            break

        if elem1 == elem2:
          result_path.append(elem1)
    return result_path


def segment_path(path, normalise=True):
    '''Segment a path into a list of components (drives, files, directories etc).

       @type path: a path
       @param path: the path to segment

       @type normalise: Boolean
       @param normalise: whether to normalise the path before starting.

       @result: a list of path segments
    '''

    if normalise:
        path = os.path.normpath(path)

    result  = []
    (head, tail) = os.path.split(path)
    if head =='' or tail == '':
        result.append(head+tail)
    else:
        while head != '' and tail != '':
            result.append(tail)
            head,tail = os.path.split(head)
        result.append(head+tail)
        result.reverse()
    return result


def join_path_segments(segments):
    '''Join a list of path segments (drives, files, directories etc) into a path.

       @type path: a list of path segments
       @param path: the path segments to join into a path

       @result: the path containing the joined path segments
    '''

    if len(segments) == 0:
        result = ''
    else:
        segments_copy = segments[:]

        segments_copy.reverse()

        result = segments_copy.pop()
        while len(segments_copy) > 0:
            result = os.path.join(result, segments_copy.pop())

    return result


class Test_finder:
    '''Find and load unit test classes as a hierarchy of TestSuites and TestCases.

       The class provides functions for running or returning the resulting
       TestSuite and requires a root directory to start searching from.

       TestCases are identified by the class name matching a pattern
       (pattern_string)
    '''

    suite = unittest.TestSuite()
    '''the root test suite to which testSuites and cases are added'''


    def __init__(self, root_path=None, pattern_string='test_.*\.py$'):
        ''' Initialise the unit test finder.

            @type root_path: a path
            @param root_path: the path to starts searching for unit tests from,
                              all sub directories and files  are searched

            @type pattern_string: a string containing a regular expression pattern
            @param pattern_string: a regular expression pattern which identifies
                                   a file as on containing a unit test TestCase
        '''

        self.root_path = root_path
        if self.root_path == None:
            self.root_path = get_startup_path()
        self.pattern = re.compile(pattern_string)
        self.paths_scanned = False


    def scan_paths(self):
        '''Scan directories and paths for unit test classes and load them into TestSuites'''

        self.suite = unittest.TestSuite()
        suite_dictionary = {'':self.suite}
        for (dir_path, dir_names, file_names) in os.walk(self.root_path):
             for file_name in file_names:
                 if self.pattern.match(file_name):

                     file_name = os.path.splitext(file_name)[0]
                     relative_module_path = get_module_relative_path(dir_path)

                     class_name = string.upper(file_name[0]) + file_name[1:]
                     if relative_module_path != '':
                         module_path = '.'.join((relative_module_path, file_name))
                     else:
                         module_path = file_name

                     modules = import_module(module_path)

                     path  = ['']
                     for i,elem in enumerate(module_path.split('.')):
                         old_path_key  =  '.'.join(path)
                         path.append(elem)
                         path_key = '.'.join(path)
                         if path_key not in suite_dictionary:
                             test_suite = unittest.TestSuite()
                             suite_dictionary[path_key]=test_suite
                             suite_dictionary[old_path_key].addTest(test_suite)

                     clazz =  getattr(modules[-1], class_name)
                     suite_dictionary[path_key].addTest(unittest.TestLoader().loadTestsFromTestCase(clazz))




#FIXME:  bad name
class Run_unit_tests(object):
    '''Class to run a particular unit test or a directory of unit tests.'''


    def __init__(self, root_path=None, test_module=None,
                 test_pattern = ['test_(\.*).py'],
                 root_system_directory = ['test_suite/unit_tests','../..'],
                 root_unit_test_directory = ['test_suite/unit_tests','.'],
                 verbose = False):
        '''Initialise the unit test runner.

          @type  root_path: a string containing a directory name
          @param root_path: root path to start searching for modules to unit test
                 from. Two special cases arise: if the string contains '.'
                 the search starts from the current working directory, if the value is
                 the special value TEST_SUITE defined in this file the root of the
                 test suite is sought from the current working directory using
                 find_unit_test_directory_path() and used instead.

          @type  test_module: string
          @param test_module: the name of a module to unit test. If the variable
                 is None a search for unit tests using <test-pattern> will start
                 form <root_path>, otherwise it will be used as a module path from the
                 current working directory.

          FIXME: rename as testcase_file_pattern
          @type  test_pattern: a list of strings containing regex patterns
          @param test_pattern: a list of regex patterns against which files will be
                 tested to see if they are expected to contain unit tests. If
                 the file has the correct pattern the module contained inside the
                 file will be searched for testCases e.g in the case of test_float.py
                 the  module to be searched for would be test_float.Test_float.

          FIXME: the following to options are search paths and should be named so
          @type  rootSystemDirectory: a list containing a directory name followed by a
                 relative path
          @param rootSystemDirectory: the directory from which the distribution
                 is rooted. This is viewed as the the 'PYTHONPATH'
                 of the classes to be tested. It must be unique and defined
                 relative to the test suite. For the current setup
                 in relax this is (\'test_suite\', /'..\'). The first string is a
                 directory to match the second string is a relative path from that
                 directory to the system directory. The search is started from the true
                 value of root_path in the file system.

          @type  root_unit_test_directory: a list containing a directory name followed by a
                 relative path
          @param root_unit_test_directory: the directory from which all unit
                 module directories descend. For the current setup in relax
                 this is (\'unit_tests\', \'.\'). The search is started from the true
                 value of root_path in the file system.

          @type  verbose: Boolean
          @param verbose: produce verbose output during testing e.g. directories
                 searched root directories etc
        '''

        self.test_module = test_module

        if self.test_module == None:
            self.test_module = os.getcwd()
        self.root_path = root_path
        if self.root_path == None:
            self.root_path = os.getcwd()
        self.test_pattern = test_pattern
        self.root_system_directory = root_system_directory
        self.root_unit_test_directory = root_unit_test_directory
        self.verbose = verbose



    def get_first_instance_path(self, path, target_directory, offset_path='.'):
        '''Get the minimal path searching down the file system totargetDirectory.

           Note the algorithm understands .. and .

            @type path:  a directory path in a string
            @param path: a directory path to search down

            @type  target_directory: a directory  name in a string
            @param target_directory: a directory to find in the path

        '''

        result = None
        seg_path = segment_path(path)
        seg_target_directory = segment_path(target_directory)
        seg_target_directory_len = len(seg_target_directory)
        #print segTargetDirectoryLen
        while len(seg_path) > 0:
           #print '\t segTargetDirectory[:-segTargetDirectoryLen] ', segTargetDirectory[-segTargetDirectoryLen:]
           #print segPath
           #print 'segPath[:-segTargetDirectoryLen]',segPath[-segTargetDirectoryLen:]
           #print
           if seg_path[-seg_target_directory_len:] == seg_target_directory[-seg_target_directory_len:]:
               break
           else:
               seg_path.pop()


        if len(seg_path) != 0:
            seg_offset_path = segment_path(offset_path)
            seg_path.extend(seg_offset_path)
            #print 'pre join', os.path.join(seg_path),seg_path
            result = os.path.normpath(join_path_segments(seg_path))

        #print 'result', result
        return result


    def find_unit_test_directory_path(self, path):
        ''' Find the path to the unit_test directory.

            The algorithm starts from path and using self.rootUnitTestDirectory to find
            the unit test directory path

             @type  path: a string containing a directory path
             @param path: a path to a point to start searching to the system
                    directory from.
        '''

        #print 'find unit test path'
        search_path = self.root_unit_test_directory[0]
        offset_path = self.root_unit_test_directory[1]
        return self.get_first_instance_path(path,search_path, offset_path)


    def find_system_directory_path(self, path):
        ''' Find the path to the relax system directory.

            The algorithm starts from path and uses self.rootSystemDirectoryto find
            the relax system directory path

             @type  path: a string containing a directory path
             @param path: a path to a point to start searching to the system
                    directory from.
        '''

        search_path = self.root_system_directory[0]
        offset_path = self.root_system_directory[1]

        return self.get_first_instance_path(path, search_path, offset_path)

    def get_module_path(self,python_module_path):
        ''' convert a module path delimited by dots into a path for
           use in the current file system

           e.g. test.python.wibble ->  test/python/wibble (under unix)

           limitationscan only currently deal with relative paths without
           backtracks non of the multidot magic for module paths introduced
           by python 2.5 pep 328 is accounted for!


           @type python_module_path: a string
           @param python_module_path: a pythond module path separated by dots

           @rtype:   string
           @return:  a (relative) path in the current file system

        '''
        elems = python_module_path.split('.')
        return os.sep.join(elems)

# FIXME: logic error two uses for self.testModule
    def paths_from_test_module(self, root_path):
        '''Determine the possible path of the self.test_module.

           The search starts from the current directory or the root_path

           The possible paths are as follows
               1. a file or directory relative to the rootPath (usually pwd)
               2. the rootPath itself (self.testModule ==  None)
               3. a file or directory relative to the unitTestRootPath
               4. the unit test directory itself (self.testModule ==  None)


           currently this assumes that if the last two names in testModule are
           the same barring an initial  capital letter in the class name
           then we can just look for the module. Thus the class name is popped
           off and we then join the moduleName together with the root unit test
           path and a '.py'

           note we can't deal with module methods...

           @type  root_path: string containing a directory name
           @param root_path: directory to start looking for the module from
        '''

        print self.test_module
        result  = []
        # first see if we can just find a direct path
        module_fs_path = self.get_module_path(self.test_module)
        test_path = os.extsep.join((module_fs_path,'py'))
        if os.path.exists(test_path):
            print 'found module: ' + module_fs_path
            result.append(test_path)
        else:

            unit_test_directory = self.find_unit_test_directory_path(root_path)
            search_paths = (unit_test_directory, root_path)
            if self.test_module != None:
                result.extend(search_paths)

            else:
                test_module_segs = string.split(self.test_module,'.')
                print 'root path', root_path
                print 'test segs', test_module_segs

                test_module_ames = []
                if len(test_module_segs) >= 2:
                    putative_class_name = test_module_segs[-1]
                    class_from_module_name = string.lower(putative_class_name[0]) + putative_class_name[:1]

                    putative_module_name = test_module_segs[-2]

                    if class_from_module_name == putative_module_name:
                        copy_test_module_segs = copy(test_module_segs)
                        class_file = copy_testModule_segs.pop()
                        class_file = class_file + '.py'
                        copy_test_module_segs.append(class_file)
                        test_module_names.append(copy_test_module_segs)

                test_module_names.append(test_module_segs)
                for test_module in test_module_names:
                    for search_path in search_paths:
                        result.append(os.path.join(search_path, test_module))

        return result


    def run(self, runner=None):
        '''Run a unit test or set of unit tests.'''

        print 'testing units...'
        print '----------------'
        print

        system_directory = self.find_system_directory_path(self.root_path)
        unit_test_directory = self.find_unit_test_directory_path(self.root_path)
        module_path = self.paths_from_test_module(self.root_path)
        if self.verbose:
            print 'root path:          ', self.root_path
            print 'system directory:   ', system_directory
            print 'unit test directory:', unit_test_directory
            for i,elem in enumerate(module_path):
                print 'module path %d:  %s'  % (i,elem)

        # add UnitTestDirectory to python path
        backup_python_path = sys.path[:]
        #sys.path.insert(1,unit_test_directory)

        # add SystemDirectory to python path
        sys.path.pop(0)
        sys.path.insert(0,system_directory)


        print sys.path

        #iterate and load unit tests from module path
        finder = Test_finder(unit_test_directory)
        finder.scan_paths()
        if runner == None:
            runner = unittest.TextTestRunner()




        # iterate and load files to be tested

        # Run the unit tests and catch the TestResult object.
        results = runner.run(finder.suite)

        # restore sys  path
        sys.path=backup_python_path

        # Return the result of all the tests.
        return results.wasSuccessful()


if __name__ == '__main__':
#    print '1',get_module_relative_path('/A/B/C', ('/A/B',))
#    print '2',get_module_relative_path('/A/B/C', ('/A/B/C',))
#    print '3',get_module_relative_path('/A/B/C', ('/A/B/D/W',))
#    print get_common_prefix(('A','B','C'), ('A','B','C'))
#    print get_common_prefix(('A','B','C'), ('A','B','C','D'))
#    print get_common_prefix(('D','E'), ('A','B','C','D'))
#    print get_common_prefix(('A','B','C','F'), ('A','B','C','D'))
#    print get_common_prefix((),('A','B','C','D'))
#    print ('A','B','C') == ('A','B','C')
    parser = OptionParser()

    parser.add_option("-v", "--verbose", dest="verbose",
                      help="verbose test ouput", default=False, action='store_true')

    usage="""
    %%prog [options] [<file-or-dir>...]

      a program to find and run subsets of the relax unit test suite using pyunit.
      (details of how to write pyunit tests can be found in your python distributions
      library reference)


    arguments:
      <file-or-dir> = <file-path> | <dir-path> is a list which can contain
                      inter-mixed directories and files

      <file-path>  =  a file containing a test case class files of the same
                      name with the first letter capitalised

                      e.g. maths_fns/test_chi2.py will be assumed to contain
                      a test case class called Test_chi2

      <dir-path>   =  a path which will be recursivley searched for <file-path>s
                      which end in %s
      """ % PY_FILE_EXTENSION

    parser.set_usage(dedent(usage))

    (options, args) = parser.parse_args()


    for arg in args:
        runner = Run_unit_tests(test_module=arg, verbose=options.verbose)
        runner.run()

#    root = tk.Tk()
#    root.title("relax unit tests")
#    gui = unitgui.TkTestRunner(root)
#    runner.run()


# todo normcase home
