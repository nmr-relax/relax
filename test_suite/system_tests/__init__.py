###############################################################################
#                                                                             #
# Copyright (C) 2006-2012 Edward d'Auvergne                                   #
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
"""The relax system/functional tests."""

# Python module imports.
from relax_errors import RelaxError
from string import split
from unittest import TestSuite

# relax system/functional test module imports.
from test_suite.relax_test_loader import RelaxTestLoader as TestLoader
from test_suite.system_tests.align_tensor import Align_tensor
from test_suite.system_tests.angles import Angles
from test_suite.system_tests.bmrb import Bmrb
from test_suite.system_tests.consistency_tests import Ct
from test_suite.system_tests.dasha import Dasha
from test_suite.system_tests.diffusion_tensor import Diffusion_tensor
from test_suite.system_tests.frame_order import Frame_order
from test_suite.system_tests.generic import Generic
from test_suite.system_tests.grace import Grace
from test_suite.system_tests.jw_mapping import Jw
from test_suite.system_tests.load_spins import Load_spins
from test_suite.system_tests.model_elimination import Modelim
from test_suite.system_tests.model_free import Mf
from test_suite.system_tests.model_selection import Modsel
from test_suite.system_tests.n_state_model import N_state_model
from test_suite.system_tests.noe import Noe
from test_suite.system_tests.noe_restraints import Noe_restraints
from test_suite.system_tests.palmer import Palmer
from test_suite.system_tests.pdc import Pdc
from test_suite.system_tests.peak_lists import Peak_lists
from test_suite.system_tests.pipes import Pipes
from test_suite.system_tests.rdc import Rdc
from test_suite.system_tests.relax_data import Relax_data
from test_suite.system_tests.relax_fit import Relax_fit
from test_suite.system_tests.results import Results
from test_suite.system_tests.sequence import Sequence
from test_suite.system_tests.state import State
from test_suite.system_tests.structure import Structure
from test_suite.system_tests.unit_vectors import Unit_vectors


__all__ = ['align_tensor',
           'angles',
           'brmb',
           'consistency_tests',
           'dasha'
           'diffusion_tensor',
           'frame_order',
           'generic',
           'grace',
           'jw_mapping',
           'load_spins',
           'model_elimination',
           'model_free',
           'model_selection',
           'n_state_model',
           'noe',
           'noe_restraints',
           'palmer',
           'pdc',
           'peak_lists'
           'pipes',
           'rdc',
           'relax_data',
           'relax_fit',
           'results',
           'scripts',
           'sequence',
           'state',
           'structure',
           'unit_vectors']


class System_test_runner:
    """Class for executing all of the system/functional tests."""

    def run(self, tests=None, runner=None):
        """Run the system/functional tests.

        The system test list should be something like ['N_state_model.test_stereochem_analysis'].  The first part is the imported test case class, the second is the specific test.


        @keyword tests:     The list of system tests to preform.
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
            suite_array.append(TestLoader().loadTestsFromTestCase(Align_tensor))
            suite_array.append(TestLoader().loadTestsFromTestCase(Bmrb))
            suite_array.append(TestLoader().loadTestsFromTestCase(Angles))
            suite_array.append(TestLoader().loadTestsFromTestCase(Ct))
            suite_array.append(TestLoader().loadTestsFromTestCase(Dasha))
            suite_array.append(TestLoader().loadTestsFromTestCase(Diffusion_tensor))
            suite_array.append(TestLoader().loadTestsFromTestCase(Frame_order))
            suite_array.append(TestLoader().loadTestsFromTestCase(Generic))
            suite_array.append(TestLoader().loadTestsFromTestCase(Grace))
            suite_array.append(TestLoader().loadTestsFromTestCase(Jw))
            suite_array.append(TestLoader().loadTestsFromTestCase(Load_spins))
            suite_array.append(TestLoader().loadTestsFromTestCase(Modelim))
            suite_array.append(TestLoader().loadTestsFromTestCase(Mf))
            suite_array.append(TestLoader().loadTestsFromTestCase(Modsel))
            suite_array.append(TestLoader().loadTestsFromTestCase(N_state_model))
            suite_array.append(TestLoader().loadTestsFromTestCase(Noe))
            suite_array.append(TestLoader().loadTestsFromTestCase(Noe_restraints))
            suite_array.append(TestLoader().loadTestsFromTestCase(Palmer))
            suite_array.append(TestLoader().loadTestsFromTestCase(Pdc))
            suite_array.append(TestLoader().loadTestsFromTestCase(Peak_lists))
            suite_array.append(TestLoader().loadTestsFromTestCase(Pipes))
            suite_array.append(TestLoader().loadTestsFromTestCase(Rdc))
            suite_array.append(TestLoader().loadTestsFromTestCase(Relax_data))
            suite_array.append(TestLoader().loadTestsFromTestCase(Relax_fit))
            suite_array.append(TestLoader().loadTestsFromTestCase(Results))
            suite_array.append(TestLoader().loadTestsFromTestCase(Sequence))
            suite_array.append(TestLoader().loadTestsFromTestCase(State))
            suite_array.append(TestLoader().loadTestsFromTestCase(Structure))
            suite_array.append(TestLoader().loadTestsFromTestCase(Unit_vectors))

        # Group all tests together.
        full_suite = TestSuite(suite_array)

        # Run the test suite.
        results = runner.run(full_suite)

        # Return the status of the tests.
        return results.wasSuccessful()
