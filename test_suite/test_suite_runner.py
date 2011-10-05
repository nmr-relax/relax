###############################################################################
#                                                                             #
# Copyright (C) 2006-2011 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
import os
import sys

# Dependency checks.
import dep_check

# Formatting.
from formatting import subtitle, summary_line, title

# Import the test suite categories.
if dep_check.wx_module:
    from gui_tests import GUI_test_runner
from system_tests import System_test_runner
from unit_tests.unit_test_runner import Unit_test_runner

# relax module imports.
from relax_test_runner import RelaxTestRunner
from status import Status; status = Status()


class Test_suite_runner:
    """Class for running all components of the relax test suite.

    This currently includes the following categories of tests:
        - System/functional tests.
        - Unit tests.
        - GUI tests.
    """

    def __init__(self, tests=[]):
        """Store the list of tests to preform.

        The test list should be something like ['N_state_model.test_stereochem_analysis'].  The first part is the imported test case class, the second is the specific test.


        @keyword tests: The list of tests to preform.  If left at [], then all tests will be run.
        @type tests:    list of str
        """

        # Store the args.
        self.tests = tests

        # A list for skipped tests.
        status.skip = []

        # Set up the test runner.
        self.runner = RelaxTestRunner(stream=sys.stdout)


    def run_all_tests(self):
        """Execute all of the test suite test types."""


        # Execute the system/functional tests.
        self.run_system_tests(summary=False)

        # Execute the unit tests.
        self.run_unit_tests(summary=False)

        # Execute the GUI tests.
        self.run_gui_tests(summary=False)

        # Print out a summary of the test suite.
        self.summary()


    def run_gui_tests(self, summary=True):
        """Execute the GUI tests.

        @keyword summary:   A flag which if True will cause a summary to be printed.
        @type summary:      bool
        """

        # Print a header.
        title('GUI tests')

        # Run the tests.
        if dep_check.wx_module:
            gui_runner = GUI_test_runner()
            self.gui_result = gui_runner.run(self.tests, runner=self.runner)

        # No wx module installed.
        else:
            print("All GUI tests skipped due to the missing/broken wx module.\n")
            self.gui_result = 'skip'

        # Print out a summary of the test suite.
        if summary:
            self.summary()


    def run_system_tests(self, summary=True):
        """Execute the system/functional tests.

        @keyword summary:   A flag which if True will cause a summary to be printed.
        @type summary:      bool
        """

        # Print a header.
        title('System / functional tests')

        # Run the tests.
        system_runner = System_test_runner()
        self.system_result = system_runner.run(self.tests, runner=self.runner)

        # Print out a summary of the test suite.
        if summary:
            self.summary()


    def run_unit_tests(self, summary=True):
        """Execute the unit tests.

        @keyword summary:   A flag which if True will cause a summary to be printed.
        @type summary:      bool
        """

        # Print a header.
        title('Unit tests')

        # Run the tests.
        unit_runner = Unit_test_runner(root_path=status.install_path+os.sep+'test_suite'+os.sep+'unit_tests')
        self.unit_result = unit_runner.run(runner=self.runner)

        # Print out a summary of the test suite.
        if summary:
            self.summary()


    def summary(self):
        """Print out a summary of the relax test suite."""

        # Title.
        title("Summary of the relax test suite")

        # The skipped tests.
        self.summary_skipped()

        # Subtitle.
        subtitle("Synopsis")

        # System/functional test summary.
        if hasattr(self, 'system_result'):
            summary_line("System/functional tests", self.system_result)

        # Unit test summary.
        if hasattr(self, 'unit_result'):
            summary_line("Unit tests", self.unit_result)

        # GUI test summary.
        if hasattr(self, 'gui_result'):
            summary_line("GUI tests", self.gui_result)

        # Synopsis.
        if hasattr(self, 'system_result') and hasattr(self, 'unit_result') and hasattr(self, 'gui_result'):
            summary_line("Synopsis", self.system_result and self.unit_result and self.gui_result)

        # End.
        print('\n\n')


    def summary_skipped(self):
        """Print out information about skipped tests.""" 

        # Counts.
        system_count = {}
        unit_count = {}
        gui_count = {}
        for i in range(len(status.skipped_tests)):
            # Alias.
            test = status.skipped_tests[i]

            # Initialise in needed.
            if not system_count.has_key(test[1]):
                system_count[test[1]] = 0
                unit_count[test[1]] = 0
                gui_count[test[1]] = 0

            # A system test.
            if test[2] == 'system':
                system_count[test[1]] += 1

            # A unit test.
            if test[2] == 'unit':
                unit_count[test[1]] += 1

            # A GUI test.
            if test[2] == 'gui':
                gui_count[test[1]] += 1

        # The missing modules.
        missing_modules = sorted(system_count.keys())
        subtitle("Optional packages/modules")

        # Nothing missing.
        if not missing_modules:
            # Print out.
            print("No tests skipped due to missing modules.\n")

            # The skip the table.
            return

        # Header.
        print("Tests skipped due to missing packages/modules:\n")
        header = "%-30s" % "Module" 
        if hasattr(self, 'system_result'):
            header = "%s %20s" % (header, "System test count")
        if hasattr(self, 'unit_result'):
            header = "%s %20s" % (header, "Unit test count")
        if hasattr(self, 'gui_result'):
            header = "%s %20s" % (header, "GUI test count")
        print('-'*len(header))
        print(header)
        print('-'*len(header))

        # The table.
        for module in missing_modules:
            text = "%-30s" % module
            if hasattr(self, 'system_result'):
                text = "%s %20s" % (text, system_count[module])
            if hasattr(self, 'unit_result'):
                text = "%s %20s" % (text, unit_count[module])
            if hasattr(self, 'gui_result'):
                text = "%s %20s" % (text, gui_count[module])
            print(text)


        # End the table.
        print('-'*len(header))
        print("\n")
