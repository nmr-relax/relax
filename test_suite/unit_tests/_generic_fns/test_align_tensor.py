###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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

# relax module imports.
from generic_fns import align_tensor
from relax_errors import RelaxStrError, RelaxUnknownParamError
from test_suite.unit_tests.align_tensor_testing_base import Align_tensor_base_class


class Test_align_tensor(Align_tensor_base_class):
    """Unit tests for the functions of the 'generic_fns.align_tensor' module."""

    # Place the generic_fns.align_tensor module into the class namespace.
    align_tensor_fns = align_tensor

    def test_return_data_name(self):
        """The returning of alignment tensor parameter names.

        The function tested is generic_fns.align_tensor.return_data_name().
        """

        # Test the return of Saupe order matrix components.
        self.assertEqual(self.align_tensor_fns.return_data_name('sxx'), 'Sxx')
        self.assertEqual(self.align_tensor_fns.return_data_name('Sxx'), 'Sxx')
        self.assertEqual(self.align_tensor_fns.return_data_name('syy'), 'Syy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Syy'), 'Syy')
        self.assertEqual(self.align_tensor_fns.return_data_name('szz'), 'Szz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Szz'), 'Szz')
        self.assertEqual(self.align_tensor_fns.return_data_name('sxy'), 'Sxy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Sxy'), 'Sxy')
        self.assertEqual(self.align_tensor_fns.return_data_name('sxz'), 'Sxz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Sxz'), 'Sxz')
        self.assertEqual(self.align_tensor_fns.return_data_name('syz'), 'Syz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Syz'), 'Syz')
        self.assertEqual(self.align_tensor_fns.return_data_name('sxxyy'), 'Sxxyy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Sxxyy'), 'Sxxyy')

        # Test the return of alignment tensor components.
        self.assertEqual(self.align_tensor_fns.return_data_name('axx'), 'Axx')
        self.assertEqual(self.align_tensor_fns.return_data_name('Axx'), 'Axx')
        self.assertEqual(self.align_tensor_fns.return_data_name('ayy'), 'Ayy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Ayy'), 'Ayy')
        self.assertEqual(self.align_tensor_fns.return_data_name('azz'), 'Azz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Azz'), 'Azz')
        self.assertEqual(self.align_tensor_fns.return_data_name('axy'), 'Axy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Axy'), 'Axy')
        self.assertEqual(self.align_tensor_fns.return_data_name('axz'), 'Axz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Axz'), 'Axz')
        self.assertEqual(self.align_tensor_fns.return_data_name('ayz'), 'Ayz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Ayz'), 'Ayz')
        self.assertEqual(self.align_tensor_fns.return_data_name('axxyy'), 'Axxyy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Axxyy'), 'Axxyy')

        # Test the return of probability matrix components.
        self.assertEqual(self.align_tensor_fns.return_data_name('pxx'), 'Pxx')
        self.assertEqual(self.align_tensor_fns.return_data_name('Pxx'), 'Pxx')
        self.assertEqual(self.align_tensor_fns.return_data_name('pyy'), 'Pyy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Pyy'), 'Pyy')
        self.assertEqual(self.align_tensor_fns.return_data_name('pzz'), 'Pzz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Pzz'), 'Pzz')
        self.assertEqual(self.align_tensor_fns.return_data_name('pxy'), 'Pxy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Pxy'), 'Pxy')
        self.assertEqual(self.align_tensor_fns.return_data_name('pxz'), 'Pxz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Pxz'), 'Pxz')
        self.assertEqual(self.align_tensor_fns.return_data_name('pyz'), 'Pyz')
        self.assertEqual(self.align_tensor_fns.return_data_name('Pyz'), 'Pyz')
        self.assertEqual(self.align_tensor_fns.return_data_name('pxxyy'), 'Pxxyy')
        self.assertEqual(self.align_tensor_fns.return_data_name('Pxxyy'), 'Pxxyy')

        # Test the return of Euler angles.
        self.assertEqual(self.align_tensor_fns.return_data_name('a'), 'alpha')
        self.assertEqual(self.align_tensor_fns.return_data_name('alpha'), 'alpha')
        self.assertEqual(self.align_tensor_fns.return_data_name('b'), 'beta')
        self.assertEqual(self.align_tensor_fns.return_data_name('beta'), 'beta')
        self.assertEqual(self.align_tensor_fns.return_data_name('g'), 'gamma')
        self.assertEqual(self.align_tensor_fns.return_data_name('gamma'), 'gamma')

        # Test a few things which should fail.
        self.assertRaises(RelaxUnknownParamError, self.align_tensor_fns.return_data_name, 'c')
        self.assertRaises(RelaxUnknownParamError, self.align_tensor_fns.return_data_name, '7')
        self.assertRaises(RelaxStrError, self.align_tensor_fns.return_data_name, 7)
        self.assertRaises(RelaxUnknownParamError, self.align_tensor_fns.return_data_name, 'tm')
