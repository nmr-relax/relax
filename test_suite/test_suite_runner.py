###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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

# Formatting.
from formatting import subtitle, summary_line, title

# Import the test suite categories.
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
    """

    def __init__(self, tests=None):
        """Store the list of tests to preform.

        The test list should be something like ['N_state_model.test_stereochem_analysis'].  The first part is the imported test case class, the second is the specific test.


        @keyword tests: The list of tests to preform.
        @type tests:    list of str
        """

        # Store the args.
        self.tests = tests

        # A list for skipped tests.
        status.skip = []


    def run_all_tests(self):
        """Execute all of the test suite test types."""


        # Execute the system/functional tests.
        self.run_system_tests(summary=False)

        # Execute the unit tests.
        self.run_unit_tests(summary=False)

        # Print out a summary of the test suite.
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
        self.system_result = system_runner.run(self.tests)

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
        self.unit_result = unit_runner.run(runner=RelaxTestRunner())

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

        # Synopsis.
        if hasattr(self, 'system_result') and hasattr(self, 'unit_result'):
            summary_line("Synopsis", self.system_result and self.unit_result)

        # End.
        print('\n\n')


    def summary_skipped(self):
        """Print out information about skipped tests.""" 

        # Counts.
        system_count = {}
        unit_count = {}
        for i in range(len(status.skipped_tests)):
            # Alias.
            test = status.skipped_tests[i]

            # Initialise in needed.
            if not system_count.has_key(test[1]):
                system_count[test[1]] = 0
                unit_count[test[1]] = 0

            # A system test.
            if test[2] == 'system':
                system_count[test[1]] += 1

            # A unit test.
            if test[2] == 'unit':
                unit_count[test[1]] += 1

        # The missing modules.
        missing_modules = system_count.keys()
        missing_modules.sort()

        # Sub-title.
        subtitle("Optional modules")

        # Nothing missing.
        if not missing_modules:
            # Print out.
            print("No tests skipped due to missing modules.\n")

            # The skip the table.
            return

        # The formatting string.
        if hasattr(self, 'system_result') and hasattr(self, 'unit_result'):
            format = "%-30s %20s %20s"
        else:
            format = "%-30s %20s"

        # Header.
        print("Tests skipped due to missing modules:\n")
        if hasattr(self, 'system_result') and hasattr(self, 'unit_result'):
            header = format % ("Module", "System test count", "Unit test count")
        elif hasattr(self, 'system_result'):
            header = format % ("Module", "System test count")
        else:
            header = format % ("Module", "Unit test count")
        print('-'*len(header))
        print(header)
        print('-'*len(header))

        # The table.
        for module in missing_modules:
            if hasattr(self, 'system_result') and hasattr(self, 'unit_result'):
                print(format % (module, system_count[module], unit_count[module]))
            elif hasattr(self, 'system_result'):
                print(format % (module, system_count[module]))
            else:
                print(format % (module, unit_count[module]))

        # End the table.
        print('-'*len(header))
        print("\n")
