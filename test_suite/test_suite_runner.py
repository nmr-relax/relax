###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
from formatting import heading, summary_line

# Import the test suite categories.
from system_tests import System_test_runner
from unit_tests.unit_test_runner import Unit_test_runner

# relax module imports.
from relax_test_runner import RelaxTestRunner


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


    def run_all_tests(self):
        """Execute all of the test suite test types."""

        # Execute the system/functional tests.
        self.run_system_tests()

        # Execute the unit tests.
        self.run_unit_tests()

        # Print out a summary of the test suite.
        self.summary()


    def run_system_tests(self):
        """Function for executing the system/functional tests."""

        # Print a header.
        heading('System / functional tests')

        # Run the tests.
        system_runner = System_test_runner()
        self.system_result = system_runner.run(self.tests)


    def run_unit_tests(self):
        """Function for executing the unit tests."""

        # Print a header.
        heading('Unit tests')

        # Run the tests.
        unit_runner = Unit_test_runner(root_path=sys.path[-1]+os.sep+'test_suite'+os.sep+'unit_tests')
        self.unit_result = unit_runner.run(runner=RelaxTestRunner())


    def summary(self):
        """Print out a summary of the relax test suite."""

        # Heading.
        print("\n\n\n")
        print("###################################")
        print("# Summary of the relax test suite #")
        print("###################################\n")

        # System/functional test summary.
        summary_line("System/functional tests", self.system_result)

        # Unit test summary.
        summary_line("Unit tests", self.unit_result)

        # Synopsis.
        summary_line("Synopsis", self.system_result and self.unit_result)
