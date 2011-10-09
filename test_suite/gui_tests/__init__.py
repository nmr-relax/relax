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

# Package docstring.
"""The relax GUI tests."""

# Python module imports.
from relax_errors import RelaxError
from string import split
from unittest import TestSuite

# relax GUI test module imports.
from model_free import Mf
from noe import Noe
from rx import Rx
from state import State
from test_suite.relax_test_loader import RelaxTestLoader as TestLoader


__all__ = ['model_free',
           'noe',
           'rx',
           'state']


class GUI_test_runner:
    """Class for executing all of the GUI tests."""

    def run(self, tests=None, runner=None):
        """Run the GUI tests.

        The GUI test list should be something like ['N_state_model.test_stereochem_analysis'].  The first part is the imported test case class, the second is the specific test.


        @keyword tests:     The list of GUI tests to preform.
        @type tests:        list of str
        @keyword runner:    A test runner such as TextTestRunner.  For an example of how to write a test runner see the python documentation for TextTestRunner in the python source.
        @type runner:       Test runner instance (TextTestRunner, BaseGUITestRunner subclass, etc.)
        """

        # Create an array of test suites (add your new TestCase classes here).
        suite_array = []

        # Specific tests.
        for test in tests:
            # Split.
            row = split(test, '.')

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
            suite_array.append(TestLoader().loadTestsFromTestCase(Mf))
            suite_array.append(TestLoader().loadTestsFromTestCase(Noe))
            suite_array.append(TestLoader().loadTestsFromTestCase(Rx))
            suite_array.append(TestLoader().loadTestsFromTestCase(State))

        # Group all tests together.
        full_suite = TestSuite(suite_array)

        # Run the test suite.
        results = runner.run(full_suite)

        # Return the status of the tests.
        return results.wasSuccessful()
