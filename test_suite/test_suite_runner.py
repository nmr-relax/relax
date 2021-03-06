###############################################################################
#                                                                             #
# Copyright (C) 2006-2008,2010-2015,2019 Edward d'Auvergne                    #
# Copyright (C) 2019 Troels Schwarz-Linnet                                    #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Dependency checks.
import dep_check

# Python module imports.
import os
import sys
from traceback import print_exc
if dep_check.wx_module:
    import wx
import unittest

# Formatting.
from test_suite.formatting import summary_line

# Import the test suite categories.
if dep_check.wx_module:
    from test_suite.gui_tests import GUI_test_runner
from test_suite.system_tests import System_test_runner
from test_suite.unit_tests.unit_test_runner import Unit_test_runner
from test_suite.verification_tests import Verification_test_runner

# relax module imports.
if dep_check.wx_module:
    from gui import relax_gui
    from gui import interpreter
from lib.text.sectioning import section, title
from test_suite.relax_test_runner import GuiTestRunner, RelaxTestRunner
from status import Status; status = Status()


class Test_suite_runner:
    """Class for running all components of the relax test suite.

    This currently includes the following categories of tests:
        - System/functional tests.
        - Unit tests.
        - GUI tests.
        - Verification tests.
    """

    def __init__(self, tests=[], from_gui=False, categories=['system', 'unit', 'gui', 'verification'], timing=False, io_capture=True, list_tests=False):
        """Store the list of tests to preform.

        The test list should be something like ['N_state_model.test_stereochem_analysis'].  The first part is the imported test case class, the second is the specific test.


        @keyword tests:         The list of tests to preform.  If left at [], then all tests will be run.
        @type tests:            list of str
        @keyword from_gui:      A flag which indicates if the tests are being run from the GUI or not.
        @type from_gui:         bool
        @keyword categories:    The list of test categories to run, for example ['system', 'unit', 'gui', 'verification'] for all tests.
        @type categories:       list of str
        @keyword timing:        A flag which if True will enable timing of individual tests.
        @type timing:           bool
        @keyword io_capture:    A flag which if True will cause all IO to be captured and only printed out for failing or error tests.
        @type io_capture:       bool
        @keyword list_tests:    A flag which if True will cause the tests to be listed rather than executed.
        @type list_tests:       bool
        """

        # Store the args.
        self.tests = tests
        self.from_gui = from_gui
        self.categories = categories
        self.list_tests = list_tests

        # Set up the test runner.
        if from_gui:
            self.runner = GuiTestRunner(stream=sys.stdout, timing=timing, io_capture=io_capture)
        else:
            self.runner = RelaxTestRunner(stream=sys.stdout, timing=timing, io_capture=io_capture)

        # Let the tests handle the keyboard interrupt (for Python 2.7 and higher).
        if hasattr(unittest, 'installHandler'):
            unittest.installHandler()


    def run_all_tests(self, reset=True):
        """Execute all of the test suite test types.

        @keyword reset:     A flag which if True will reset the relax status objects for the tests.
        @type reset:        bool
        @return:            The combined status of the test categories.
        @rtype:             bool
        """

        # Reset the list for skipped tests.
        if reset:
            status.skipped_tests = []

        # Store the status, so that all test categories are run.
        test_status = True

        # Execute the system/functional tests.
        if 'system' in self.categories:
            test_status = self.run_system_tests(summary=False, reset=False) and test_status

        # Execute the unit tests.
        if 'unit' in self.categories:
            test_status = self.run_unit_tests(summary=False, reset=False) and test_status

        # Execute the GUI tests.
        if 'gui' in self.categories:
            test_status = self.run_gui_tests(summary=False, reset=False) and test_status

        # Execute the software verification tests.
        if 'verification' in self.categories:
            test_status = self.run_verification_tests(summary=False, reset=False) and test_status

        # Print out a summary of the test suite and return the combined status.
        if not self.list_tests:
            self.summary()
        return test_status


    def run_gui_tests(self, summary=True, reset=True):
        """Execute the GUI tests.

        @keyword summary:   A flag which if True will cause a summary to be printed.
        @type summary:      bool
        @keyword reset:     A flag which if True will reset the relax status objects for the tests.
        @type reset:        bool
        @return:            True if the tests were run, False if a KeyboardInterrupt occurred.
        @rtype:             bool
        """

        # Reset the list for skipped tests.
        if reset:
            status.skipped_tests = []

        # Run the tests, catching the keyboard interrupt.
        try:
            # Print a header.
            title(file=sys.stdout, text='GUI tests')

            # Run the tests.
            if dep_check.wx_module:
                # Set up the GUI if needed (i.e. not in GUI mode already).
                app = wx.GetApp()
                if app == None:
                    # Initialise.
                    app = wx.App(redirect=False)

                    # Build the GUI.
                    app.gui = relax_gui.Main(parent=None, id=-1, title="")

                # Execute the GUI tests.
                gui_runner = GUI_test_runner()
                self.runner.category = 'gui'
                self.gui_result = gui_runner.run(self.tests, runner=self.runner, list_tests=self.list_tests)

                # Clean up for the GUI, if not in GUI mode.
                if status.test_mode:
                    # Terminate the interpreter thread to allow the tests to cleanly exit.
                    interpreter_thread = interpreter.Interpreter()
                    interpreter_thread.exit()

                    # Stop the GUI main loop.
                    app.ExitMainLoop()

            # No wx module installed.
            else:
                print("All GUI tests skipped due to the missing/broken wx module.\n")
                self.gui_result = 'skip'

            # Print out a summary of the test suite.
            if summary and not self.list_tests:
                self.summary()

        # Catch the keyboard interrupt.
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt:  Terminating all tests.\n")
            sys.exit(1)

        # Catch GUI app set up errors.
        except:
            print("Failure in setting up the GUI tests.\n")
            print_exc()
            if summary and not self.list_tests:
                self.summary()
            self.gui_result = 'skip'
            return False

        # All tests were run successfully.
        return self.gui_result


    def run_system_tests(self, summary=True, reset=True):
        """Execute the system/functional tests.

        @keyword summary:   A flag which if True will cause a summary to be printed.
        @type summary:      bool
        @keyword reset:     A flag which if True will reset the relax status objects for the tests.
        @type reset:        bool
        @return:            True if the tests were run, False if a KeyboardInterrupt occurred.
        @rtype:             bool
        """

        # Reset the list for skipped tests.
        if reset:
            status.skipped_tests = []

        # Run the tests, catching the keyboard interrupt.
        try:
            # Print a header.
            title(file=sys.stdout, text='System / functional tests')

            # Run the tests.
            system_runner = System_test_runner()
            self.runner.category = 'system'
            self.system_result = system_runner.run(self.tests, runner=self.runner, list_tests=self.list_tests)

            # Print out a summary of the test suite.
            if summary and not self.list_tests:
                self.summary()

        # Catch the keyboard interrupt.
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt:  Terminating all tests.\n")
            sys.exit(1)

        # All tests were run successfully.
        return self.system_result


    def run_unit_tests(self, summary=True, reset=True):
        """Execute the unit tests.

        @keyword summary:   A flag which if True will cause a summary to be printed.
        @type summary:      bool
        @keyword reset:     A flag which if True will reset the relax status objects for the tests.
        @type reset:        bool
        @return:            True if the tests were run, False if a KeyboardInterrupt occurred.
        @rtype:             bool
        """

        # Reset the list for skipped tests.
        if reset:
            status.skipped_tests = []

        # Run the tests, catching the keyboard interrupt.
        try:
            # Print a header.
            title(file=sys.stdout, text='Unit tests')

            # Run the tests.
            unit_runner = Unit_test_runner(root_path=status.install_path+os.sep+'test_suite'+os.sep+'unit_tests')
            self.runner.category = 'unit'
            self.unit_result = unit_runner.run(self.tests, runner=self.runner, list_tests=self.list_tests)

            # Print out a summary of the test suite.
            if summary and not self.list_tests:
                self.summary()

        # Catch the keyboard interrupt.
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt:  Terminating all tests.\n")
            sys.exit(1)

        # All tests were run successfully.
        return self.unit_result


    def run_verification_tests(self, summary=True, reset=True):
        """Execute the software verification tests.

        @keyword summary:   A flag which if True will cause a summary to be printed.
        @type summary:      bool
        @keyword reset:     A flag which if True will reset the relax status objects for the tests.
        @type reset:        bool
        """

        # Reset the list for skipped tests.
        if reset:
            status.skipped_tests = []

        # Run the tests, catching the keyboard interrupt.
        try:
            # Print a header.
            title(file=sys.stdout, text='Software verification tests')

            # Run the tests.
            verification_runner = Verification_test_runner()
            self.runner.category = 'verification'
            self.verification_result = verification_runner.run(self.tests, runner=self.runner, list_tests=self.list_tests)

            # Print out a summary of the test suite.
            if summary and not self.list_tests:
                self.summary()

        # Catch the keyboard interrupt.
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt:  Terminating all tests.\n")
            sys.exit(1)

        # All tests were run successfully.
        return self.verification_result


    def summary(self):
        """Print out a summary of the relax test suite."""

        # Title.
        title(file=sys.stdout, text="Summary of the relax test suite")

        # The skipped tests.
        if status.skip_blacklisted_tests:
            self.summary_skipped()

        # Subtitle.
        section(file=sys.stdout, text="Synopsis")

        # System/functional test summary.
        if hasattr(self, 'system_result'):
            summary_line("System/functional tests", self.system_result, width=status.text_width)

        # Unit test summary.
        if hasattr(self, 'unit_result'):
            summary_line("Unit tests", self.unit_result, width=status.text_width)

        # GUI test summary.
        if hasattr(self, 'gui_result'):
            summary_line("GUI tests", self.gui_result, width=status.text_width)

        # Verification test summary.
        if hasattr(self, 'verification_result'):
            summary_line("Software verification tests", self.verification_result, width=status.text_width)

        # Synopsis.
        if hasattr(self, 'system_result') and hasattr(self, 'unit_result') and hasattr(self, 'gui_result') and hasattr(self, 'verification_result'):
            if self.gui_result == "skip":
                test_status = self.system_result and self.unit_result and self.verification_result
            else:
                test_status = self.system_result and self.unit_result and self.gui_result and self.verification_result
            summary_line("Synopsis", test_status, width=status.text_width)

        # End.
        print('\n\n')


    def summary_skipped(self):
        """Print out information about skipped tests.""" 

        # Counts.
        system_count = {}
        unit_count = {}
        gui_count = {}
        verification_count = {}
        for i in range(len(status.skipped_tests)):
            # Alias.
            test = status.skipped_tests[i]

            # Skip all skipped tests whereby the module is set to None to indicate that the test skipping should not be reported.
            if test[1] == None:
                continue

            # Initialise in needed.
            if not test[1] in system_count:
                system_count[test[1]] = 0
                unit_count[test[1]] = 0
                gui_count[test[1]] = 0
                verification_count[test[1]] = 0

            # A system test.
            if test[2] == 'system':
                system_count[test[1]] += 1

            # A unit test.
            if test[2] == 'unit':
                unit_count[test[1]] += 1

            # A GUI test.
            if test[2] == 'gui':
                gui_count[test[1]] += 1

            # A verification test.
            if test[2] == 'verification':
                verification_count[test[1]] += 1

        # The missing modules.
        missing_modules = sorted(system_count.keys())
        section(file=sys.stdout, text="Optional packages/modules")

        # Nothing missing.
        if not missing_modules:
            # Except for the wx module!
            if not dep_check.wx_module and hasattr(self, 'gui_result'):
                print("All GUI tests skipped due to the missing wxPython module, no other tests skipped due to missing modules.\n")

            # Normal printout.
            else:
                print("No tests skipped due to missing modules.\n")

            # The skip the table.
            return

        # Header.
        print("Tests skipped due to missing optional packages/modules/software:\n")
        header = "%-33s" % "Module/package/software" 
        if len(system_count):
            header = "%s %20s" % (header, "System test count")
        if len(unit_count):
            header = "%s %20s" % (header, "Unit test count")
        if len(gui_count):
            header = "%s %20s" % (header, "GUI test count")
        if len(verification_count):
            header = "%s %20s" % (header, "Verification test count")
        print('-'*len(header))
        print(header)
        print('-'*len(header))

        # The table.
        for module in missing_modules:
            text = "%-33s" % module
            if len(system_count):
                text = "%s %20s" % (text, system_count[module])
            if len(unit_count):
                text = "%s %20s" % (text, unit_count[module])
            if len(gui_count):
                text = "%s %20s" % (text, gui_count[module])
            if len(verification_count):
                text = "%s %20s" % (text, verification_count[module])
            print(text)

        # End the table.
        print('-'*len(header))
        print("\n")
