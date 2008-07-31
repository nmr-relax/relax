###############################################################################
#                                                                             #
# Copyright (C) 2006, 2008 Edward d'Auvergne                                  #
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
from unittest import TestLoader, TestSuite

# relax module imports.
from test_suite.relax_test_runner import RelaxTestRunner

# relax system/functional test module imports.
from angles import Angles
from consistency_tests import Ct
from dasha import Dasha
from diffusion_tensor import Diffusion_tensor
from generic import Generic
from jw_mapping import Jw
from load_spins import Load_spins
from model_free import Mf
from model_selection import Modsel
from n_state_model import N_state_model
from nmrview import NMRView
from palmer import Palmer
from pipe_create import Pipe_create
from relax_fit import Relax_fit
from results import Results
from sequence import Sequence


__all__ = ['angles',
           'consistency_tests',
           'dasha'
           'diffusion_tensor',
           'generic',
           'jw_mapping',
           'load_spins',
           'model_free',
           'model_selection',
           'n_state_model',
           'nmrview',
           'palmer',
           'pipe_create',
           'relax_fit',
           'results',
           'sequence']


class System_test_runner:
    """Class for executing all of the system/functional tests."""

    def __init__(self, relax):
        """Place the relax namespace into self.relax when instantiating the class.

        @param relax:   The relax namespace.
        @type relax:    instance
        """

        self.relax = relax


    def run(self):
        """Function for running all of the system/functional tests."""

        # Create an array of test suites (add your new TestCase classes here).
        suite_array = []
        suite_array.append(TestLoader().loadTestsFromTestCase(Angles))
        suite_array.append(TestLoader().loadTestsFromTestCase(Ct))
        suite_array.append(TestLoader().loadTestsFromTestCase(Dasha))
        suite_array.append(TestLoader().loadTestsFromTestCase(Diffusion_tensor))
        suite_array.append(TestLoader().loadTestsFromTestCase(Generic))
        suite_array.append(TestLoader().loadTestsFromTestCase(Jw))
        suite_array.append(TestLoader().loadTestsFromTestCase(Load_spins))
        suite_array.append(TestLoader().loadTestsFromTestCase(Mf))
        suite_array.append(TestLoader().loadTestsFromTestCase(Modsel))
        suite_array.append(TestLoader().loadTestsFromTestCase(N_state_model))
        suite_array.append(TestLoader().loadTestsFromTestCase(NMRView))
        suite_array.append(TestLoader().loadTestsFromTestCase(Palmer))
        suite_array.append(TestLoader().loadTestsFromTestCase(Pipe_create))
        suite_array.append(TestLoader().loadTestsFromTestCase(Relax_fit))
        suite_array.append(TestLoader().loadTestsFromTestCase(Results))
        suite_array.append(TestLoader().loadTestsFromTestCase(Sequence))

        # Add the relax namespace to each TestCase object.
        for i in xrange(len(suite_array)):
            for test in suite_array[i]._tests:
                test.relax = self.relax

        # Group all tests together.
        full_suite = TestSuite(suite_array)

        # Run the test suite.
        results = RelaxTestRunner().run(full_suite)

        # Return the status of the tests.
        return results.wasSuccessful()
