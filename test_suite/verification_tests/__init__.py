###############################################################################
#                                                                             #
# Copyright (C) 2006-2014 Edward d'Auvergne                                   #
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

# Package docstring.
"""The relax software verification tests.

For a description of verification tests, please see U{Wikipedia<https://en.wikipedia.org/wiki/Verification_and_validation_%28software%29>}.
"""

# Python module imports.
from re import search
from unittest import TestSuite

# relax module imports.
from lib.errors import RelaxError

# relax software verification test module imports.
from test_suite.relax_test_loader import RelaxTestLoader as TestLoader
from test_suite.verification_tests.library import Library
from test_suite.verification_tests.status_object import Status_object


__all__ = [
    'library',
    'status_object'
]


class Verification_test_runner:
    """Class for executing all of the software verification tests."""

    def run(self, tests=None, runner=None):
        """Run the software verification tests.

        @keyword tests:     The list of system tests to preform.
        @type tests:        list of str
        @keyword runner:    A test runner such as TextTestRunner.  For an example of how to write a test runner see the python documentation for TextTestRunner in the python source.
        @type runner:       Test runner instance (TextTestRunner, BaseGUITestRunner subclass, etc.)
        """

        # Create an array of test suites (add your new TestCase classes here).
        suite_array = []

        # Specific tests.
        for test in tests:
            # The entire test class.
            if not search('\.', test):
                # Check that the class exists.
                if test not in globals():
                    raise RelaxError("The system test class '%s' does not exist." % test)

                # The uninstantiated class object.
                obj = globals()[test]

                # Add the tests.
                suite_array.append(TestLoader().loadTestsFromTestCase(obj))

            # Single system test.
            else:
                # Split.
                row = test.split('.')

                # Check.
                if len(row) != 2:
                    raise RelaxError("The test '%s' is not in the correct format.  It should consist of the test case class, a dot, and the specific test." % test)

                # Unpack.
                class_name, test_name = row

                # Get the class object.
                obj = globals()[class_name]

                # Add the test.
                suite_array.append(TestLoader().loadTestsFromNames([test_name], obj))

        # All tests.
        if not tests:
            suite_array.append(TestLoader().loadTestsFromTestCase(Library))
            suite_array.append(TestLoader().loadTestsFromTestCase(Status_object))

        # Group all tests together.
        full_suite = TestSuite(suite_array)

        # Run the test suite.
        results = runner.run(full_suite)

        # Return the status of the tests.
        return results.wasSuccessful()
