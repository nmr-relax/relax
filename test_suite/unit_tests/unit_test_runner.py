#!/usr/bin/env python
################################################################################
#                                                                              #
# Copyright (C) 2006-2007  Gary S Thompson                                     #
#                         (see https://gna.org/users/varioustoxins             #
#                                      for contact details)                    #
#                                                                              #
# Copyright (C) 2007-2011 Edward d'Auvergne                                    #
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

# Module docstring.
"""Utilities for unit test running from the command line or within the relax testing frame work.

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

A concrete example: for class <relax-root-directory>/maths-fns/chi2.py FIXME:***complete***


The framework can discover sets of unit tests from the file system and add
them to TestSuites either from the command line or programmatically from
inside another program. It also has the ability to search for a  root unit
test and system directory from a position anywhere inside the unit test
hierarchy.

TODO: Examine PEP 338 and runpy.run_module(modulename): Executing Modules as Scripts for a later
version of relax that is dependant on python 2.5.
TODO: Split out runner part from search part.
"""

from copy import copy
import os, re, string, sys, unittest, traceback
from optparse import OptionParser
from textwrap import dedent

# relax module imports.
try:
    from test_suite.relax_test_loader import RelaxTestLoader as TestLoader
except ImportError:
    from unittest import TestLoader


# constants
###########

PY_FILE_EXTENSION='.py'


# utility functions
###################


def get_startup_path():
    """Get the path of the directory the program started from.

    The startup path is the first path in sys.path (the internal PYTHONPATH) by convention. If the
    first element of sys.path is an empty trying the current working directory is used instead.

    @return:    A file system path for the current operating system.
    @rtype:     str
    """

    startup_path = sys.path[0]
    if startup_path == '':
        startup_path = os.getcwd()
    return startup_path


def import_module(module_path):
    """Import the python module named by module_path.

    @param module_path: A module path in python dot separated format.  Note: this currently doesn't
                        support relative module paths as defined by pep328 and python 2.5.
    @type module_path:  str
    @return:            The module path as a list of module instances or None if the module path
                        cannot be found in the python path.
    @rtype:             list of class module instances or None
    """

    module = None
    result = None

    #try:
    module = __import__(module_path)
    #except:
    #    print 'failed'
    #    sys.exit()

    if module != None:
        result = [module]
        components = module_path.split('.')
        for component in components[1:]:
            module = getattr(module, component)
            result.append(module)
    return result


def get_module_relative_path(package_path, module_name, root_paths=None):
    """Find the relative path of a module to one of a set of root paths using a list of package paths and a module name.

    As the module may match more than one path the first path that can contain it is chosen.

    @param package_path:    Path of a python packages leading to module_name.
    @type  package_path:    str
    @param module_name:     The name of the module to load.
    @type module_name:      str
    @keyword root_paths:    A set of paths to search for the module in.  If None is passed the list
                            is initialized from the internal PYTHONPATH sys.path.  Elements which
                            are empty strings are replace with the current working directory
                            sys.getcwd().
    @type root_paths:       list of str
    @return:                A relative module path to one of the rootPaths which is separated by
                            '.'s if the modulePath is a subpath of one of the root paths, otherwise
                            None.
    @rtype:                 str or None
    """

    relative_path = None
    if root_paths == None:
        root_paths = sys.path
    for root_path in root_paths:
        root_path = segment_path(os.path.abspath(root_path))

        # Catch if the package path has already been converted to a segment list.
        if not isinstance(package_path, list):
            package_path = segment_path(os.path.abspath(package_path))

        common_prefix = get_common_prefix(root_path, package_path)
        if common_prefix == root_path:
            relative_path = package_path[len(common_prefix):]
            break

    if relative_path != None:
        relative_path = '.'.join(relative_path)

        if relative_path != '':
            relative_path = '.'.join((relative_path, module_name))
        else:
            relative_path = module_name



    return relative_path


def get_common_prefix(path1, path2):
    """Get the common prefix between two paths.

    @param path1:   The first path to be compared.
    @type path1:    list of str
    @param path2:   The second path to be compared.
    @type path2:    list of str
    @return:        The common path shared between the two paths starting from the root directory as
                    a list of segments.  If there is no common path an empty list is returned.
    @rtype:         list of str
    """

    result_path = []
    for elem1, elem2 in map(None, path1, path2):
        if elem1 == None or elem2 == None:
            break

        if elem1 == elem2:
          result_path.append(elem1)
    return result_path


def segment_path(path, normalise=True):
    """Segment a path into a list of components (drives, files, directories etc).

    @param path:        The path to segment.
    @type path:         str
    @param normalise:   Whether to normalise the path before starting.
    @type normalise:    bool
    @return:            A list of path segments.
    @rtype:             list of str
    """

    if normalise:
        path = os.path.normpath(path)

    result  = []
    (head, tail) = os.path.split(path)
    if head =='' or tail == '':
        result.append(head+tail)
    else:
        while head != '' and tail != '':
            result.append(tail)
            head, tail = os.path.split(head)
        result.append(head+tail)
        result.reverse()
    return result


def join_path_segments(segments):
    """Join a list of path segments (drives, files, directories etc) into a path.

    @param segments:    The path segments to join into a path.
    @type segments:     a list of path segments
    @return:            The path containing the joined path segments.
    @rtype:             str
    """

    if len(segments) == 0:
        result = ''
    else:
        segments_copy = segments[:]

        segments_copy.reverse()

        result = segments_copy.pop()
        while len(segments_copy) > 0:
            result = os.path.join(result, segments_copy.pop())

    return result



class ImportErrorTestCase(unittest.TestCase):
    """TestCase class for nicely handling import errors."""

    def __init__(self, module_name, message):
        """Set up the import error class.

        @param module_name: The module which could not be imported.
        @type module_name:  str
        @param message:     The formatted traceback message (e.g. from traceback.format_exc()).
        @type message:      str
        """

        # Execute the base class __init__() method.
        super(ImportErrorTestCase, self).__init__('testImportError')

        # Store the info for printing out at the end of the unit tests.
        self.module_name = module_name
        self.message = message


    def testImportError(self):
        """Unit test module import."""

        # First print out the module to allow it to be identified and debugged.
        print("\nImport of the %s module.\n" % self.module_name)

        # Fail!
        self.fail(self.message)


def load_test_case(package_path, module_name, class_name):
    """Load a testCase from the file system using a package path, file name and class name.

    @param package_path:    Full system path of the module file.
    @type package_path:     str
    @param module_name:     Name of the module to load the class from.
    @type module_name:      str
    @param class_name:      Name of the class to load.
    @type class_name:       str
    @return:                The suite of test cases.
    @rtype:                 TestSuite instance
    """

    # Determine the full name of the module.
    module = get_module_relative_path(package_path, module_name)

    # Catch import errors, adding the ImportErrorTestCase class to the test suite.
    try:
        packages = import_module(module)
    except:
        # Initialise a test suite.
        suite = unittest.TestSuite()

        # Add the ImportErrorTestCase.
        suite.addTest(ImportErrorTestCase(module, traceback.format_exc()))

        # Return the suite.
        return suite

    # Nothing to do.
    if not packages:
        return

    # Some input packages may not contain the required class.
    if not hasattr(packages[-1], class_name):
        return

    # Get the class object.
    clazz = getattr(packages[-1], class_name)

    # Load the test cases and return the suite of test cases.
    return TestLoader().loadTestsFromTestCase(clazz)



class Test_finder:
    """Find and load unit test classes as a hierarchy of TestSuites and TestCases.

    The class provides functions for running or returning the resulting TestSuite and requires a
    root directory to start searching from.

    TestCases are identified by the class name matching a pattern (pattern_string).
    """

    suite = unittest.TestSuite()
    """The root test suite to which testSuites and cases are added."""

    def __init__(self, root_path=None, pattern_list=[]):
        """Initialise the unit test finder.

        @keyword root_path:     The path to starts searching for unit tests from, all sub
                                directories and files are searched.
        @type root_path:        str
        @keyword pattern_list:  A list of regular expression patterns which identify a file as one
                                containing a unit test TestCase.
        @type pattern_list:     list of str
        """

        self.root_path = root_path
        if self.root_path == None:
            self.root_path = get_startup_path()
        self.patterns=[]
        for pattern in pattern_list:
            self.patterns.append(re.compile(pattern))
        self.paths_scanned = False


    def scan_paths(self):
        """Scan directories and paths for unit test classes and load them into TestSuites."""

        # Initialise the TestSuite object.
        self.suite = unittest.TestSuite()

        # Loop over all directories recursively.
        for (dir_path, dir_names, file_names) in os.walk(self.root_path):
            # Loop over the files.
            for file_name in file_names:
                # Is the file part of the test.
                module_found = False
                for pattern in self.patterns:
                    if pattern.match(file_name):
                        module_found = True
                        break

                # If not, skip the file.
                if not module_found:
                    continue

                # Build the class name from the file name.
                module_name = os.path.splitext(file_name)[0]
                class_name = string.upper(module_name[0]) + module_name[1:]

                # Load the test case into the test suite.
                test_case = load_test_case(dir_path, module_name, class_name)
                if test_case != None:
                    self.suite.addTest(test_case)



class Unit_test_runner(object):
    """Class to run a particular unit test or a directory of unit tests."""

    #constants
    system_path_pattern = ['test_suite' + os.sep + 'unit_tests', os.pardir + os.sep + os.pardir]
    """@ivar:   A search template for the directory in which relax is installed.  The directory which relax is installed in is viewed as the the 'PYTHONPATH' of the classes to be tested. It must be unique and defined relative to the test suite. For the current setup in relax this is (\'test_suite\', /'..\'). The first string is a directory structure to match the second string is a relative path from that directory to the system directory. The search is started from the value of root_path in the file system.
       @type:  list of str
    """

    unit_test_path_pattern = ['test_suite' + os.sep + 'unit_tests', os.curdir]
    """@ivar:   A search template for the directory from which all unit module directories descend. For the current setup in relax this is (\'unit_tests\', \'.\'). The search is started from the value of root_path in the file system.
       @type:   list of str
    """

    test_case_patterns = ['test_.*\.py$']
    """@ivar:   A list of regex patterns against which files will be
                tested to see if they are expected to contain unit tests. If
                the file has the correct pattern the module contained inside the
                file will be searched for testCases e.g in the case of test_float.py
                the module to be searched for would be test_float.Test_float.
       @type:   list of str
    """

    def __init__(self, root_path=os.curdir, test_module=None, search_for_root_path=True, search_for_unit_test_path=True, verbose=False):
        """Initialise the unit test runner.

        @keyword root_path:                 Root path to start searching for modules to unit test from.  If the string contains '.' the search starts from the current working directory.  Default current working directory.
        @type root_path:                    str
        @keyword test_module:               The name of a module to unit test. If the variable is None a search for all unit tests using <test-pattern> will start from <root_path>, if the variable is '.' a search for all unit tests will commence from the current working directory, otherwise it will be used as a module path from the current root_path or CHECKME: ****module_directory_path****. The module name can be in the directory path format used by the current operating system or a unix style path with /'s including a final .py extension or a dotted moudle name.
        @type test_module:                  str
        @keyword search_for_root_path:      Whether to carry out a search from the root_directory using self.system_path_pattern to find the directory self.system_directory if no search is carried out self.system_directory is set to None and it is the responsibility of code creating the class to set it before self.run is called.
        @type search_for_root_path:         bool
        @keyword search_for_unit_test_path: Whether to carry out a search from the root_directory using self.unit_test_path_patter to find the directory self.unit_test_directory if no search is carried out self.unit_test_directory is set to None and it is the responsibility of code creating the class to set it before self.run is called.
        @type search_for_unit_test_path:    bool
        @keyword verbose:                   Produce verbose output during testing e.g. directories searched root directories etc.
        @type verbose:                      bool
        """

        # The root path is the current working directory (translate to the full path).
        if root_path == os.curdir:
            root_path = os.getcwd()

        # Store the root path.
        self.root_path = root_path

        # Verbose print out.
        if ((search_for_root_path) == True or (search_for_unit_test_path == True)) and verbose:
            print('searching for paths')
            print('-------------------')
            print('')

        # Find system directories or leave it for someone else as needed.
        if search_for_root_path:
            self.system_directory = self.get_first_instance_path(root_path, self.system_path_pattern[0], self.system_path_pattern[1])

            if self.system_directory == None:
                raise Exception("can't find system directory start from %s" % root_path)
            else:
                if verbose:
                    print(('search for system directory found:    %s' % self.system_directory))
        else:
            self.system_directory = None

        if search_for_unit_test_path:
            self.unit_test_directory = self.get_first_instance_path(root_path, self.unit_test_path_pattern[0], self.unit_test_path_pattern[1])
            if self.unit_test_directory == None:
                raise Exception("can't find unit test directory start from %s" % root_path)
            else:
                if verbose:
                    print(('search for unit test directory found: %s' % self.unit_test_directory))
        else:
            self.unit_test_directory = None

        # Deal with test_module.
        if test_module == None:
            test_module = self.root_path
        elif test_module == os.curdir:
            test_module =  os.getcwd()
        elif test_module == self.TEST_SUITE_ROOT:
            test_module = self.unit_test_directory

        self.test_module = test_module

        # Other instance variables.
        self.verbose = verbose


    def get_first_instance_path(self, path, target_path, offset_path=os.curdir):
        """Get the minimal path searching up the file system to target_directory.

        The algorithm is that we repeatedly chop the end off path and see if the tail of the path matches target_path If it doesn't match we search in the resulting directory by appending target_path and seeing if it exists in the file system. Finally once the required directory structure has been found the offset_path is appended to the found path and the resulting path normalised.

        Note the algorithm understands .. and .


        @param path:            A directory path to search up.
        @type path:             str
        @param target_path:     A directory to find in the path or below one of the elements in the path.
        @type target_path:      str
        @keyword offset_path:   A relative path offset to add to the path that has been found to give the result directory.
        @type offset_path:      str
        @return:                The path that has been found or None if the path cannot be found by walking up and analysing the current directory structure.
        @rtype:                 str
        """

        seg_path = segment_path(os.path.normpath(path))
        seg_target_directory = segment_path(target_path)
        seg_target_directory_len = len(seg_target_directory)

        found_seg_path = None
        while len(seg_path) > 0 and found_seg_path == None:
           if seg_path[-seg_target_directory_len:] == seg_target_directory[-seg_target_directory_len:]:
               found_seg_path = seg_path
               break
           else:
               extended_seg_path = copy(seg_path)
               extended_seg_path.extend(seg_target_directory)
               if os.path.exists(os.path.join(*extended_seg_path)):
                   found_seg_path = extended_seg_path
                   break

           seg_path.pop()

        result = None
        if found_seg_path != None and len(found_seg_path) != 0:
            seg_offset_path = segment_path(offset_path)
            found_seg_path.extend(seg_offset_path)
            result = os.path.normpath(join_path_segments(found_seg_path))

        return result


    def paths_from_test_module(self, test_module):
        """Determine the possible paths of the test_module.

        It is assumed that the test_module can be either a path or a python module or package name including dots.

        The following heuristics are used:

            1. If the test_module=None add the value '.'.
            2. If the test_module ends with a PY_FILE_EXTENSION append test_module with the PY_FILE_EXTENSION removed.
            3. Add the module_name with .'s converted to /'s and any elements of the form PY_FILE_EXTENSION removed.
            4. Repeat 2 and 3 with the last element of the path repeated with the first letter capitalised.

        Note: we can't deal with module methods...


        @return:    A set of possible module names in python '.' separated format.
        @rtype:     str
        """

        result = set()

        # check for current working directory
        if test_module == None:
            result.add(os.curdir)
        else:
            # add a direct file
            mpath = []
            test_module_segments = segment_path(test_module)
            for elem in test_module_segments:
                if elem.endswith(PY_FILE_EXTENSION):
                    mpath.append(os.path.splitext(elem)[0])
                else:
                    mpath.append(elem)

            result.add(tuple(mpath))

            mpath = copy(mpath)
            mpath.append(mpath[-1].capitalize())
            result.add(tuple(mpath))

            module_path_elems = test_module.split('.')

            module_norm_path = []
            for elem in module_path_elems:
                if elem != PY_FILE_EXTENSION[1:]:
                    module_norm_path.append(elem)

            # See if we can find a dot separated module.
            # a package name first
            elems_ok = True
            for elem in module_norm_path:
                if len(segment_path(elem)) > 1:
                    elems_ok = False
                    break

            if elems_ok:
                result.add(tuple(module_norm_path))

                mpath = copy(module_norm_path)
                mpath.append(module_norm_path[-1].capitalize())
                result.add(tuple(mpath))

        return result


    def run(self, runner=None):
        """Run a unit test or set of unit tests.

        @keyword runner:    A unit test runner such as TextTestRunner.  None indicates use of the default unit test runner.  For an example of how to write a test runner see the python documentation for TextTestRunner in the python source.
        @type runner:       Unit test runner instance (TextTestRunner, BaseGUITestRunner subclass, etc.)
        @return:            A string indicating success or failure of the unit tests run.
        @rtype:             str
        """

        msg = "Either set self.%s to a %s directory or set search_for_%s_path in self.__init__ to True"
        if self.unit_test_directory ==  None:
            raise Exception(msg % ('unit_test_directory', 'unit test', 'unit_test'))
        if self.system_directory == None:
            raise Exception(msg % ('system_directory', 'system', 'root'))

        # Title printout.
        if self.verbose:
            print('testing units...')
            print('----------------')
            print('')

        module_paths = self.paths_from_test_module(self.test_module)
        if self.verbose:
            print(('root path:          ', self.root_path))
            print(('system directory:   ', self.system_directory))
            print(('unit test directory:', self.unit_test_directory))
            print('')
            for i, elem in enumerate(module_paths):
                print(('module path %d:  %s'  % (i, elem)))
            print('')

        # add SystemDirectory to python path
        sys.path.pop(0)
        sys.path.insert(0, self.system_directory)

        tests = None

        # use search path first
        for module_path in module_paths:
            module_string = os.path.join(*module_path)

            if os.path.isdir(module_string):
                #iterate and load unit tests from module path
                finder = Test_finder(module_string, self.test_case_patterns)
                finder.scan_paths()
                tests = finder.suite
                break

        # Execute specific tests.
        if tests == None:
            for module_path in module_paths:
                print(module_path)
                path_len = len(module_path)
                if path_len <= 1:
                    continue
                elif path_len == 2:
                    print(('trying to load 2: ',  module_path[0], module_path[1]))
                    tests = load_test_case('', module_path[0], module_path[1])
                else:
                    print(('trying to load 3: ', os.path.join(*module_path[:-2]), module_path[-2], module_path[-1]))
                    tests = load_test_case(os.path.join(*module_path[:-2]), module_path[-2], module_path[-1])
                if tests != None:
                    break

        if runner == None:
            runner = unittest.TextTestRunner()

        if self.verbose:
            print('results')
            print('-------')
            print('')

        # Run the unit tests and catch the TestResult object.
        if tests != None and tests.countTestCases() != 0:
            # Run the test.
            results = runner.run(tests)
            result_string = results.wasSuccessful()

        elif tests == None:
            results = None
            result_string = 'Error: no test directories found for input module: %s' % self.test_module
            print(result_string)
        else:
            results = None
            result_string = 'note: no tests found for input module: %s' % self.test_module
            print(result_string)

        # Return the result of all the tests.
        return result_string



# Command line usage.
if __name__ == '__main__':
    # Set up the parser options.
    parser = OptionParser()
    parser.add_option("-v", "--verbose", dest="verbose", help="verbose test ouput", default=False, action='store_true')
    parser.add_option("-u", "--system", dest="system_directory", help="path to relax top directory which contains test_suite", default=None)
    parser.add_option("-s", "--utest", dest="unit_test_directory", help="default unit test directory", default=None)

    # Set the help string.
    usage = """
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
                      which end in "*.py".
      """
    parser.set_usage(dedent(usage))

    # Parse the args.
    (options, args) = parser.parse_args()

    # Initalise some flags.
    search_system = True
    search_unit = True

    # The system directory.
    if options.system_directory != None:
        if not os.path.exists(options.system_directory):
            print("The path to the system directory doeesn't exist")
            print(("provided path: %s" % options.system_directory))
            print("exiting...")
            sys.exit(0)
        search_system = False

    # A unit test directory.
    if options.unit_test_directory != None:
        if not os.path.exists(options.unit_test_directory):
            print("The path to the system directory doeesn't exist")
            print(("provided path: %s" % options.unit_test_directory))
            print("exiting...")
            sys.exit(0)
        search_unit = False

    # No arguments.
    if len(args) < 1:
        args = [None]

    # Loop over the arguments.
    for arg in args:
        # Initialise the unit test runner.
        runner = Unit_test_runner(test_module=arg, verbose=options.verbose, search_for_unit_test_path=search_unit, search_for_root_path=search_system)

        # Add the system directory to the runner.
        if not search_system:
            runner.system_directory = options.system_directory

        # Add the unit test directory to the runner.
        if not search_unit:
            runner.unit_test_directory = options.unit_test_directory

        # Execute the tests.
        runner.run()
