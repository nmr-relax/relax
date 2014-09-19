###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_MMQ_CR72, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_R1RHO_3SITE
from specific_analyses.relax_disp.variables import MODEL_EXP_TYPE, MODEL_EQ, MODEL_PARAMS, MODEL_SITES, MODEL_YEAR
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_variables(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.variables module."""


    def test_MODEL_PARAMS(self):
        """Unit test of the MODEL_PARAM dictionary."""

        # Test parameter return from model parameter dictionary.
        params_cr72 = MODEL_PARAMS[MODEL_CR72]

        # Test the return.
        self.assertEqual(params_cr72, ['r2', 'pA', 'dw', 'kex'])


    def test_MODEL_YEAR(self):
        """Unit test of the MODEL_YEAR dictionary."""

        # Test model year return from model year dictionary.
        year_cr72 = MODEL_YEAR[MODEL_CR72]

        # Test the return.
        self.assertEqual(year_cr72, 1972)


    def test_MODEL_EXP_TYPE(self):
        """Unit test of the MODEL_EXP_TYPE dictionary."""

        # Test model year return from model year dictionary.
        exp_type_mmq_cr72 = MODEL_EXP_TYPE[MODEL_MMQ_CR72]

        # Test the return.
        self.assertEqual(exp_type_mmq_cr72, 'CPMG: SQ, DQ, MQ, ZQ, 1H SQ, 1H MQ')


    def test_MODEL_SITES(self):
        """Unit test of the MODEL_SITES dictionary."""

        # Test model chemical sites return from model sites dictionary.
        model_sites = MODEL_SITES[MODEL_NS_R1RHO_3SITE]

        # Test the return.
        self.assertEqual(model_sites, 3)


    def test_MODEL_EQ(self):
        """Unit test of the MODEL_EQ dictionary."""

        # Test model equation type return from model equation dictionary.
        model_eq = MODEL_EQ[MODEL_NS_CPMG_2SITE_EXPANDED]

        # Test the return.
        self.assertEqual(model_eq, 'silico')


