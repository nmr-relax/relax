###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# relax module imports.
from specific_analyses.relax_disp.variables import MODEL_CR72
from specific_analyses.relax_disp.variables import MODEL_PARAMS
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_variables(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.variables module."""


    def test_MODEL_PARAMS(self):
        """Unit test of the MODEL_PARAM dictionary."""

        # Test parameter return from model parameter dictionary.
        params_cr72 = MODEL_PARAMS[MODEL_CR72]

        # Test the return.
        self.assertEqual(params_cr72, ['r2', 'pA', 'dw', 'kex'])

