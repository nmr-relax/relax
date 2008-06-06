###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from math import cos, pi, sin
from numpy import array, dot, transpose
from unittest import TestCase

# relax module imports.
from data.align_tensor import AlignTensorData, AlignTensorSimList
from generic_fns.align_tensor import kappa
from relax_errors import RelaxError


class Test_align_tensor(TestCase):
    """Unit tests for the data.align_tensor relax module."""

    def calc_objects(self, Sxx, Syy, Sxy, Sxz, Syz):
        """Function for calculating the alignment tensor objects."""

        # The parameter values.
        Szz = - Sxx - Syy
        Sxxyy = Sxx - Syy

        # Matrices.
        tensor = array([[ Sxx, Sxy, Sxz],
                        [ Sxy, Syy, Syz],
                        [ Sxz, Syz, Szz]])

        # Return the objects.
        return Szz, Sxxyy, tensor


    def setUp(self):
        """Set 'self.align_data' to an empty instance of the AlignTensorData class."""

        self.align_data = AlignTensorData('test')


    def test_append_sim(self):
        """Test the appending of Monte Carlo simulation alignment tensor parameters.

        The following parameters will be appended to empty lists:
            Axx: -16.6278 Hz
            Ayy: 6.13037 Hz
            Axy: 7.65639 Hz
            Axz: -1.89157 Hz
            Ayz: 19.2561 Hz
        """

        # The MC sim parameter values.
        Sxx = 3.0/2.0 * -16.6278 / kappa() * 1.02e-10**3
        Syy = 3.0/2.0 * 6.13037 / kappa() * 1.02e-10**3
        Sxy = 3.0/2.0 * 7.65639 / kappa() * 1.02e-10**3
        Sxz = 3.0/2.0 * -1.89157 / kappa() * 1.02e-10**3
        Syz = 3.0/2.0 * 19.2561 / kappa() * 1.02e-10**3

        # Set the MC sim alignment parameter lists.
        self.align_data.Sxx_sim = AlignTensorSimList('Sxx', self.align_data)
        self.align_data.Syy_sim = AlignTensorSimList('Syy', self.align_data)
        self.align_data.Sxy_sim = AlignTensorSimList('Sxy', self.align_data)
        self.align_data.Sxz_sim = AlignTensorSimList('Sxz', self.align_data)
        self.align_data.Syz_sim = AlignTensorSimList('Syz', self.align_data)

        # Append the values.
        self.align_data.Sxx_sim.append(Sxx)
        self.align_data.Syy_sim.append(Syy)
        self.align_data.Sxy_sim.append(Sxy)
        self.align_data.Sxz_sim.append(Sxz)
        self.align_data.Syz_sim.append(Syz)

        # Test the set values.
        self.assertEqual(self.align_data.Sxx_sim[0], Sxx)
        self.assertEqual(self.align_data.Syy_sim[0], Syy)
        self.assertEqual(self.align_data.Sxy_sim[0], Sxy)
        self.assertEqual(self.align_data.Sxz_sim[0], Sxz)
        self.assertEqual(self.align_data.Syz_sim[0], Syz)

        # Calculate the diffusion tensor objects.
        Szz, Sxxyy, tensor = self.calc_objects(Sxx, Syy, Sxy, Sxz, Syz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Szz_sim[0], Szz)
        self.assertEqual(self.align_data.Sxxyy_sim[0], Sxxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor_sim[0].tostring(), tensor.tostring())


    def test_set_Szz(self):
        """Test that the Szz parameter cannot be set."""

        # Assert that a RelaxError occurs when Szz is set.
        self.assertRaises(RelaxError, setattr, self.align_data, 'Szz', -23.0)

        # Make sure that the Szz parameter has not been set.
        self.assert_(not hasattr(self.align_data, 'Szz'))


    def test_set_errors(self):
        """Test the setting of spheroidal diffusion tensor parameter errors.

        The following parameter errors will be set:
            Axx: 0.3 Hz
            Ayy: 0.5 Hz
            Axy: 0.4 Hz
            Axz: 0.1 Hz
            Ayz: 0.2 Hz
        """

        # The parameter errors.
        Sxx = 3.0/2.0 * 0.3 / kappa() * 1.02e-10**3
        Syy = 3.0/2.0 * 0.5 / kappa() * 1.02e-10**3
        Sxy = 3.0/2.0 * 0.4 / kappa() * 1.02e-10**3
        Sxz = 3.0/2.0 * 0.1 / kappa() * 1.02e-10**3
        Syz = 3.0/2.0 * 0.2 / kappa() * 1.02e-10**3

        # Set the diffusion parameters.
        self.align_data.Sxx_err = Sxx
        self.align_data.Syy_err = Syy
        self.align_data.Sxy_err = Sxy
        self.align_data.Sxz_err = Sxz
        self.align_data.Syz_err = Syz

        # Test the set values.
        self.assertEqual(self.align_data.Sxx_err, Sxx)
        self.assertEqual(self.align_data.Syy_err, Syy)
        self.assertEqual(self.align_data.Sxy_err, Sxy)
        self.assertEqual(self.align_data.Sxz_err, Sxz)
        self.assertEqual(self.align_data.Syz_err, Syz)

        # Calculate the diffusion tensor objects.
        Szz, Sxxyy, tensor = self.calc_objects(Sxx, Syy, Sxy, Sxz, Syz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Szz_err, Szz)
        self.assertEqual(self.align_data.Sxxyy_err, Sxxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor_err.tostring(), tensor.tostring())


    def test_set_params(self):
        """Test the setting of alignment tensor parameters.

        The following parameters will be set:
            Axx: -16.6278 Hz
            Ayy: 6.13037 Hz
            Axy: 7.65639 Hz
            Axz: -1.89157 Hz
            Ayz: 19.2561 Hz
        """

        # The parameter values.
        Sxx = 3.0/2.0 * -16.6278 / kappa() * 1.02e-10**3
        Syy = 3.0/2.0 * 6.13037 / kappa() * 1.02e-10**3
        Sxy = 3.0/2.0 * 7.65639 / kappa() * 1.02e-10**3
        Sxz = 3.0/2.0 * -1.89157 / kappa() * 1.02e-10**3
        Syz = 3.0/2.0 * 19.2561 / kappa() * 1.02e-10**3

        # Set the diffusion parameters.
        self.align_data.Sxx = Sxx
        self.align_data.Syy = Syy
        self.align_data.Sxy = Sxy
        self.align_data.Sxz = Sxz
        self.align_data.Syz = Syz

        # Test the set values.
        self.assertEqual(self.align_data.Sxx, Sxx)
        self.assertEqual(self.align_data.Syy, Syy)
        self.assertEqual(self.align_data.Sxy, Sxy)
        self.assertEqual(self.align_data.Sxz, Sxz)
        self.assertEqual(self.align_data.Syz, Syz)

        # Calculate the diffusion tensor objects.
        Szz, Sxxyy, tensor = self.calc_objects(Sxx, Syy, Sxy, Sxz, Syz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Szz, Szz)
        self.assertEqual(self.align_data.Sxxyy, Sxxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor.tostring(), tensor.tostring())


    def test_set_sim(self):
        """Test the setting of Monte Carlo simulation alignment tensor parameters.

        Firstly the following parameters will be appended to empty lists:
            Axx: -16.6278 Hz
            Ayy: 6.13037 Hz
            Axy: 7.65639 Hz
            Axz: -1.89157 Hz
            Ayz: 19.2561 Hz

        These MC sim values will then be explicity overwritten by setting the first elements of the
        lists to:
            Axx: 0.3 Hz
            Ayy: 0.5 Hz
            Axy: 0.4 Hz
            Axz: 0.1 Hz
            Ayz: 0.2 Hz
        """

        # Set the MC sim alignment parameter lists.
        self.align_data.Sxx_sim = AlignTensorSimList('Sxx', self.align_data)
        self.align_data.Syy_sim = AlignTensorSimList('Syy', self.align_data)
        self.align_data.Sxy_sim = AlignTensorSimList('Sxy', self.align_data)
        self.align_data.Sxz_sim = AlignTensorSimList('Sxz', self.align_data)
        self.align_data.Syz_sim = AlignTensorSimList('Syz', self.align_data)

        # Append the initial values.
        self.align_data.Sxx_sim.append(3.0/2.0 * -16.6278 / kappa() * 1.02e-10**3)
        self.align_data.Syy_sim.append(3.0/2.0 * 6.13037 / kappa() * 1.02e-10**3)
        self.align_data.Sxy_sim.append(3.0/2.0 * 7.65639 / kappa() * 1.02e-10**3)
        self.align_data.Sxz_sim.append(3.0/2.0 * -1.89157 / kappa() * 1.02e-10**3)
        self.align_data.Syz_sim.append(3.0/2.0 * 19.2561 / kappa() * 1.02e-10**3)

        # The new MC sim parameter values.
        Sxx = 3.0/2.0 * 0.3 / kappa() * 1.02e-10**3
        Syy = 3.0/2.0 * 0.5 / kappa() * 1.02e-10**3
        Sxy = 3.0/2.0 * 0.4 / kappa() * 1.02e-10**3
        Sxz = 3.0/2.0 * 0.1 / kappa() * 1.02e-10**3
        Syz = 3.0/2.0 * 0.2 / kappa() * 1.02e-10**3

        # Set the MC sim parameter values (overwriting the initial values).
        self.align_data.Sxx_sim[0] = Sxx
        self.align_data.Syy_sim[0] = Syy
        self.align_data.Sxy_sim[0] = Sxy
        self.align_data.Sxz_sim[0] = Sxz
        self.align_data.Syz_sim[0] = Syz

        # Test the set values.
        self.assertEqual(self.align_data.Sxx_sim[0], Sxx)
        self.assertEqual(self.align_data.Syy_sim[0], Syy)
        self.assertEqual(self.align_data.Sxy_sim[0], Sxy)
        self.assertEqual(self.align_data.Sxz_sim[0], Sxz)
        self.assertEqual(self.align_data.Syz_sim[0], Syz)

        # Calculate the diffusion tensor objects.
        Szz, Sxxyy, tensor = self.calc_objects(Sxx, Syy, Sxy, Sxz, Syz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Szz_sim[0], Szz)
        self.assertEqual(self.align_data.Sxxyy_sim[0], Sxxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor_sim[0].tostring(), tensor.tostring())


    def test_set_Sxx(self):
        """Test the setting of the Sxx parameter."""

        # Set the Sxx value to 0.0001.
        self.align_data.Sxx = 0.0001

        # Test that the Sxx parameter has been set correctly.
        self.assert_(hasattr(self.align_data, 'Sxx'))
        self.assertEqual(self.align_data.Sxx, 0.0001)
