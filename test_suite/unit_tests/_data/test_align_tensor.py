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
from Numeric import array, dot, transpose
from unittest import TestCase

# relax module imports.
from data.align_tensor import AlignTensorData, AlignTensorSimList
from relax_errors import RelaxError


class Test_align_tensor(TestCase):
    """Unit tests for the data.align_tensor relax module."""

    def calc_objects(self, Axx, Ayy, Axy, Axz, Ayz):
        """Function for calculating the alignment tensor objects."""

        # The parameter values.
        Azz = 1.0 - Axx - Ayy
        Axxyy = Axx - Ayy

        # Matrices.
        tensor_diag = array([[ Axx,  0.0,  0.0],
                             [  0.0, Ayy,  0.0],
                             [  0.0,  0.0, Azz]])

        # Return the objects.
        return Azz, Axxyy, tensor_diag


    def setUp(self):
        """Set 'self.align_data' to an empty instance of the AlignTensorData class."""

        self.align_data = AlignTensorData()


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
        Axx = -16.6278
        Ayy = 6.13037
        Axy = 7.65639
        Axz = -1.89157
        Ayz = 19.2561

        # Set the MC sim alignment parameter lists.
        self.align_data.Axx_sim = AlignTensorSimList('Axx', self.align_data)
        self.align_data.Ayy_sim = AlignTensorSimList('Ayy', self.align_data)
        self.align_data.Axy_sim = AlignTensorSimList('Axy', self.align_data)
        self.align_data.Axz_sim = AlignTensorSimList('Axz', self.align_data)
        self.align_data.Ayz_sim = AlignTensorSimList('Ayz', self.align_data)

        # Append the values.
        self.align_data.Axx_sim.append(Axx)
        self.align_data.Ayy_sim.append(Ayy)
        self.align_data.Axy_sim.append(Axy)
        self.align_data.Axz_sim.append(Axz)
        self.align_data.Ayz_sim.append(Ayz)

        # Test the set values.
        self.assertEqual(self.align_data.Axx_sim[0], Axx)
        self.assertEqual(self.align_data.Ayy_sim[0], Ayy)
        self.assertEqual(self.align_data.Axy_sim[0], Axy)
        self.assertEqual(self.align_data.Axz_sim[0], Axz)
        self.assertEqual(self.align_data.Ayz_sim[0], Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor_diag = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz_sim[0], Azz)
        self.assertEqual(self.align_data.Axxyy_sim[0], Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor_diag_sim[0].tostring(), tensor_diag.tostring())


    def test_set_Azz(self):
        """Test that the Azz parameter cannot be set."""

        # Assert that a RelaxError occurs when Azz is set.
        self.assertRaises(RelaxError, setattr, self.align_data, 'Azz', -23.0)

        # Make sure that the Azz parameter has not been set.
        self.assert_(not hasattr(self.align_data, 'Azz'))


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
        Axx = 0.3
        Ayy = 0.5
        Axy = 0.4
        Axz = 0.1
        Ayz = 0.2

        # Set the diffusion parameters.
        self.align_data.Axx_err = Axx
        self.align_data.Ayy_err = Ayy
        self.align_data.Axy_err = Axy
        self.align_data.Axz_err = Axz
        self.align_data.Ayz_err = Ayz

        # Test the set values.
        self.assertEqual(self.align_data.Axx_err, Axx)
        self.assertEqual(self.align_data.Ayy_err, Ayy)
        self.assertEqual(self.align_data.Axy_err, Axy)
        self.assertEqual(self.align_data.Axz_err, Axz)
        self.assertEqual(self.align_data.Ayz_err, Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor_diag = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz_err, Azz)
        self.assertEqual(self.align_data.Axxyy_err, Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor_diag_err.tostring(), tensor_diag.tostring())


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
        Axx = -16.6278
        Ayy = 6.13037
        Axy = 7.65639
        Axz = -1.89157
        Ayz = 19.2561

        # Set the diffusion parameters.
        self.align_data.Axx = Axx
        self.align_data.Ayy = Ayy
        self.align_data.Axy = Axy
        self.align_data.Axz = Axz
        self.align_data.Ayz = Ayz

        # Test the set values.
        self.assertEqual(self.align_data.Axx, Axx)
        self.assertEqual(self.align_data.Ayy, Ayy)
        self.assertEqual(self.align_data.Axy, Axy)
        self.assertEqual(self.align_data.Axz, Axz)
        self.assertEqual(self.align_data.Ayz, Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor_diag = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz, Azz)
        self.assertEqual(self.align_data.Axxyy, Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor_diag.tostring(), tensor_diag.tostring())


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
        self.align_data.Axx_sim = AlignTensorSimList('Axx', self.align_data)
        self.align_data.Ayy_sim = AlignTensorSimList('Ayy', self.align_data)
        self.align_data.Axy_sim = AlignTensorSimList('Axy', self.align_data)
        self.align_data.Axz_sim = AlignTensorSimList('Axz', self.align_data)
        self.align_data.Ayz_sim = AlignTensorSimList('Ayz', self.align_data)

        # Append the initial values.
        self.align_data.Axx_sim.append(-16.6278)
        self.align_data.Ayy_sim.append(6.13037)
        self.align_data.Axy_sim.append(7.65639)
        self.align_data.Axz_sim.append(-1.89157)
        self.align_data.Ayz_sim.append(19.2561)

        # The new MC sim parameter values.
        Axx = 0.3
        Ayy = 0.5
        Axy = 0.4
        Axz = 0.1
        Ayz = 0.2

        # Set the MC sim parameter values (overwriting the initial values).
        self.align_data.Axx_sim[0] = Axx
        self.align_data.Ayy_sim[0] = Ayy
        self.align_data.Axy_sim[0] = Axy
        self.align_data.Axz_sim[0] = Axz
        self.align_data.Ayz_sim[0] = Ayz

        # Test the set values.
        self.assertEqual(self.align_data.Axx_sim[0], Axx)
        self.assertEqual(self.align_data.Ayy_sim[0], Ayy)
        self.assertEqual(self.align_data.Axy_sim[0], Axy)
        self.assertEqual(self.align_data.Axz_sim[0], Axz)
        self.assertEqual(self.align_data.Ayz_sim[0], Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor_diag = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz_sim[0], Azz)
        self.assertEqual(self.align_data.Axxyy_sim[0], Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.tensor_diag_sim[0].tostring(), tensor_diag.tostring())


    def test_set_Axx(self):
        """Test the setting of the Axx parameter."""

        # Set the Axx value to 10 Hz.
        self.align_data.Axx = 10.0

        # Test that the Axx parameter has been set correctly.
        self.assert_(hasattr(self.align_data, 'Axx'))
        self.assertEqual(self.align_data.Axx, 10.0)
