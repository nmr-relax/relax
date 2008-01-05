###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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
from unittest import TestLoader, TextTestRunner

# relax module imports.
from test_pipe_create import Test_pipe_create
from test_suite.relax_test_runner import RelaxTestRunner


__all__ = ['angles',
           'diffusion_tensor',
           'generic.py',
           'jw_mapping',
           'main',
           'model_free',
           'model_selection',
           'test_pipe_create',
           'relax_fit',
           'run_create',
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

        # Create the test suite (add your new classes here).
        suite = TestLoader().loadTestsFromTestCase(Test_pipe_create)

        # Add the relax namespace to each TestCase object.
        for test in suite._tests:
            test.relax = self.relax

        # Run the test suite.
        TextTestRunner().run(suite)
