###############################################################################
#                                                                             #
# Copyright (C) 2006,2008-2012,2019 Edward d'Auvergne                         #
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
"""The relax GUI tests."""

# Python module imports.
from re import search
from unittest import TestSuite
import wx

# relax module imports.
from lib.errors import RelaxError

# relax GUI test module imports.
from test_suite.formatting import format_test_name
from test_suite.gui_tests.bmrb import Bmrb
from test_suite.gui_tests.bruker import Bruker
from test_suite.gui_tests.consistency_tests import Ct
from test_suite.gui_tests.dead_uf_pages import Dead_uf_pages
from test_suite.gui_tests.frame_order import Frame_order
from test_suite.gui_tests.general import General
from test_suite.gui_tests.interatomic import Interatomic
from test_suite.gui_tests.jw_mapping import Jw_mapping
from test_suite.gui_tests.model_free import Mf
from test_suite.gui_tests.n_state_model import N_state_model
from test_suite.gui_tests.noe import Noe
from test_suite.gui_tests.pipes import Pipes
from test_suite.gui_tests.relax_disp import Relax_disp
from test_suite.gui_tests.rx import Rx
from test_suite.gui_tests.state import State
from test_suite.gui_tests.test_user_functions import User_functions
from test_suite.relax_test_loader import RelaxTestLoader as TestLoader


__all__ = ['bmrb',
           'consistency_tests',
           'gui',
           'interatomic',
           'jw_mapping',
           'model_free',
           'n_state_model',
           'noe',
           'pipes',
           'rx',
           'state']


class GUI_test_runner:
    """Class for executing all of the GUI tests."""

    def run(self, tests=None, runner=None, list_tests=False):
        """Run the GUI tests.

        The GUI test list should be something like ['N_state_model.test_stereochem_analysis'].  The first part is the imported test case class, the second is the specific test.


        @keyword tests:         The list of GUI tests to preform.
        @type tests:            list of str
        @keyword runner:        A test runner such as TextTestRunner.  For an example of how to write a test runner see the python documentation for TextTestRunner in the python source.
        @type runner:           Test runner instance (TextTestRunner, BaseGUITestRunner subclass, etc.)
        @keyword list_tests:    A flag which if True will cause the tests to be listed rather than executed.
        @type list_tests:       bool
        """

        # Create an array of test suites (add your new TestCase classes here).
        suite_array = []

        # Specific tests.
        for test in tests:
            # The entire test class.
            if not search(r'\.', test):
                # Check that the class exists.
                if test not in globals():
                    raise RelaxError("The GUI test class '%s' does not exist." % test)

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
                    raise RelaxError("The GUI test '%s' is not in the correct format.  It should consist of the test case class, a dot, and the specific test." % test)

                # Unpack.
                class_name, test_name = row

                # Get the class object.
                obj = globals()[class_name]

                # Add the test.
                suite_array.append(TestLoader().loadTestsFromNames([test_name], obj))

        # All tests.
        if not tests:
            suite_array.append(TestLoader().loadTestsFromTestCase(Bmrb))
            suite_array.append(TestLoader().loadTestsFromTestCase(Bruker))
            suite_array.append(TestLoader().loadTestsFromTestCase(Ct))
            suite_array.append(TestLoader().loadTestsFromTestCase(Dead_uf_pages))
            suite_array.append(TestLoader().loadTestsFromTestCase(Frame_order))
            suite_array.append(TestLoader().loadTestsFromTestCase(General))
            suite_array.append(TestLoader().loadTestsFromTestCase(Interatomic))
            suite_array.append(TestLoader().loadTestsFromTestCase(Jw_mapping))
            suite_array.append(TestLoader().loadTestsFromTestCase(Mf))
            suite_array.append(TestLoader().loadTestsFromTestCase(N_state_model))
            suite_array.append(TestLoader().loadTestsFromTestCase(Noe))
            suite_array.append(TestLoader().loadTestsFromTestCase(Pipes))
            suite_array.append(TestLoader().loadTestsFromTestCase(Relax_disp))
            suite_array.append(TestLoader().loadTestsFromTestCase(Rx))
            suite_array.append(TestLoader().loadTestsFromTestCase(State))
            suite_array.append(TestLoader().loadTestsFromTestCase(User_functions))

        # Group all tests together.
        full_suite = TestSuite(suite_array)

        # Only list the tests.
        if list_tests:
            for suite in full_suite._tests:
                for test in suite:
                    print(format_test_name(test.id()))
            return True

        # Run the test suite.
        results = runner.run(full_suite)

        # Return the status of the tests.
        return results.wasSuccessful()
