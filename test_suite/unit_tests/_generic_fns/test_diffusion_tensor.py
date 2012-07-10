###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Python module imports.
from unittest import TestCase

# relax module imports.
from generic_fns import diffusion_tensor
from relax_errors import RelaxStrError
from test_suite.unit_tests.diffusion_tensor_testing_base import Diffusion_tensor_base_class



class Test_diffusion_tensor(Diffusion_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'generic_fns.diffusion_tensor' module."""

    # Place the generic_fns.diffusion_tensor module into the class namespace.
    diffusion_tensor_fns = diffusion_tensor


    def test_return_data_name(self):
        """The returning of diffusion tensor parameter names.

        The function tested is generic_fns.diffusion_tensor.return_data_name().
        """

        # Test the return of diffusion tensor Eigenvalue components.
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('tm'), 'tm')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('diso'), 'Diso')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Diso'), 'Diso')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('da'), 'Da')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Da'), 'Da')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('dr'), 'Dr')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Dr'), 'Dr')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('dx'), 'Dx')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Dx'), 'Dx')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('dy'), 'Dy')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Dy'), 'Dy')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('dz'), 'Dz')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Dz'), 'Dz')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('dpar'), 'Dpar')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Dpar'), 'Dpar')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('dper'), 'Dper')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Dper'), 'Dper')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('dratio'), 'Dratio')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('Dratio'), 'Dratio')

        # Test the return of Euler and spherical angles.
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('a'), 'alpha')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('alpha'), 'alpha')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('b'), 'beta')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('beta'), 'beta')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('g'), 'gamma')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('gamma'), 'gamma')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('theta'), 'theta')
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('phi'), 'phi')

        # Test a few things which should fail.
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('c'), None)
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('7'), None)
        self.assertRaises(RelaxStrError, self.diffusion_tensor_fns.return_data_name, 7)
        self.assertEqual(self.diffusion_tensor_fns.return_data_name('tmm'), None)
