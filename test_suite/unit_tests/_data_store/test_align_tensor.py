###############################################################################
#                                                                             #
# Copyright (C) 2007-2008,2010,2012,2014 Edward d'Auvergne                    #
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

# Python module imports.
from numpy import array
from unittest import TestCase

# relax module imports.
from data_store.align_tensor import AlignTensorData
from pipe_control.align_tensor import kappa
from lib.errors import RelaxError


class Test_align_tensor(TestCase):
    """Unit tests for the data.align_tensor relax module."""

    def calc_objects(self, Axx, Ayy, Axy, Axz, Ayz):
        """Function for calculating the alignment tensor objects."""

        # The parameter values.
        Azz = - Axx - Ayy
        Axxyy = Axx - Ayy

        # Matrices.
        tensor = array([[ Axx, Axy, Axz],
                        [ Axy, Ayy, Ayz],
                        [ Axz, Ayz, Azz]])

        # Return the objects.
        return Azz, Axxyy, tensor


    def setUp(self):
        """Set 'self.align_data' to an empty instance of the AlignTensorData class."""

        self.align_data = AlignTensorData('test')


    def test_append_sim(self):
        """Test the appending of Monte Carlo simulation alignment tensor parameters.

        The following parameters will be appended to empty lists:
            - Axx: -16.6278 Hz
            - Ayy: 6.13037 Hz
            - Axy: 7.65639 Hz
            - Axz: -1.89157 Hz
            - Ayz: 19.2561 Hz
        """

        # The MC sim parameter values.
        Axx = -16.6278 / kappa() * 1.02e-10**3
        Ayy = 6.13037 / kappa() * 1.02e-10**3
        Axy = 7.65639 / kappa() * 1.02e-10**3
        Axz = -1.89157 / kappa() * 1.02e-10**3
        Ayz = 19.2561 / kappa() * 1.02e-10**3

        # Set the number of MC sims.
        self.align_data.set_sim_num(1)

        # Set the values.
        self.align_data.set(param='Axx', value=Axx, category='sim', sim_index=0)
        self.align_data.set(param='Ayy', value=Ayy, category='sim', sim_index=0)
        self.align_data.set(param='Axy', value=Axy, category='sim', sim_index=0)
        self.align_data.set(param='Axz', value=Axz, category='sim', sim_index=0)
        self.align_data.set(param='Ayz', value=Ayz, category='sim', sim_index=0)

        # Test the set values.
        self.assertEqual(self.align_data.Axx_sim[0], Axx)
        self.assertEqual(self.align_data.Ayy_sim[0], Ayy)
        self.assertEqual(self.align_data.Axy_sim[0], Axy)
        self.assertEqual(self.align_data.Axz_sim[0], Axz)
        self.assertEqual(self.align_data.Ayz_sim[0], Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz_sim[0], Azz)
        self.assertEqual(self.align_data.Axxyy_sim[0], Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.A_sim[0].tostring(), tensor.tostring())


    def test_irreducible_params(self):
        """Test the irreducible parameters {A-2, A-1, A0, A1, A2}.

        This is to test if the Pales results can be matched.  The example is::

            DATA SAUPE_MATRIX     S(zz)       S(xx-yy)      S(xy)      S(xz)      S(yz)
            DATA SAUPE        -1.2856e-04 -5.6870e-04 -3.1704e-04  3.5099e-04 -1.7937e-04
            DATA IRREDUCIBLE_REP    A0          A1R          A1I         A2R         A2I  
            DATA IRREDUCIBLE    -2.0380e-04 -4.5433e-04 -2.3218e-04 -3.6807e-04  4.1038e-04
            DATA IRREDUCIBLE GENERAL_MAGNITUDE   1.0816e-03
        """

        # From Pales (S(zz)       S(xx-yy)      S(xy)      S(xz)      S(yz))
        Azz = 2.0 / 3.0 * -1.2856e-04
        Axxyy = 2.0 / 3.0 * -5.6870e-04
        Axy = 2.0 / 3.0 * -3.1704e-04
        Axz = 2.0 / 3.0 * 3.5099e-04
        Ayz = 2.0 / 3.0 * -1.7937e-04

        # Parameter conversion.
        Axx = (Axxyy - Azz) / 2.0
        Ayy = (-Axxyy - Azz) / 2.0

        # Set the values.
        self.align_data.set(param='Axx', value=Axx)
        self.align_data.set(param='Ayy', value=Ayy)
        self.align_data.set(param='Axy', value=Axy)
        self.align_data.set(param='Axz', value=Axz)
        self.align_data.set(param='Ayz', value=Ayz)

        # Pales equivalent printout.
        print("Pales output:\n")
        print("DATA SAUPE_MATRIX     S(zz)       S(xx-yy)      S(xy)      S(xz)      S(yz)")
        print("DATA SAUPE        -1.2856e-04 -5.6870e-04 -3.1704e-04  3.5099e-04 -1.7937e-04")
        print("")
        print("DATA IRREDUCIBLE_REP    A0          A1R          A1I         A2R         A2I  ")
        print("DATA IRREDUCIBLE    -2.0380e-04 -4.5433e-04 -2.3218e-04 -3.6807e-04  4.1038e-04")
        print("DATA IRREDUCIBLE GENERAL_MAGNITUDE   1.0816e-03")
        print("")
        print("Calculated values:\n")
        print("A0:    %15.4e" % self.align_data.A0)
        print("A1:    %15.4e %11.4ei" % (self.align_data.A1.real, self.align_data.A1.imag))
        print("Am1:   %15.4e %11.4ei" % (self.align_data.Am1.real, self.align_data.Am1.imag))
        print("A2:    %15.4e %11.4ei" % (self.align_data.A2.real, self.align_data.A2.imag))
        print("Am2:   %15.4e %11.4ei" % (self.align_data.Am2.real, self.align_data.Am2.imag))

        # Check that the values match Pales (guessing that Pales is using the negative indices).
        self.assertAlmostEqual(self.align_data.A0, -2.0380e-04)
        self.assertAlmostEqual(self.align_data.A1.real, 4.5433e-04)
        self.assertAlmostEqual(self.align_data.A1.imag, -2.3218e-04)
        self.assertAlmostEqual(self.align_data.Am1.real, -4.5433e-04)
        self.assertAlmostEqual(self.align_data.Am1.imag, -2.3218e-04)
        self.assertAlmostEqual(self.align_data.A2.real, -3.6807e-04)
        self.assertAlmostEqual(self.align_data.A2.imag, -4.1038e-04)
        self.assertAlmostEqual(self.align_data.Am2.real, -3.6807e-04)
        self.assertAlmostEqual(self.align_data.Am2.imag, 4.1038e-04)


    def test_set_Szz(self):
        """Test that the Szz parameter cannot be set."""

        # Assert that a RelaxError occurs when Szz is set.
        self.assertRaises(RelaxError, setattr, self.align_data, 'Szz', -23.0)

        # Make sure that the Szz parameter has not been set.
        self.assertTrue(not hasattr(self.align_data, 'Szz'))


    def test_set_errors(self):
        """Test the setting of spheroidal diffusion tensor parameter errors.

        The following parameter errors will be set:
            - Axx: 0.3 Hz
            - Ayy: 0.5 Hz
            - Axy: 0.4 Hz
            - Axz: 0.1 Hz
            - Ayz: 0.2 Hz
        """

        # The parameter errors.
        Axx = 0.3 / kappa() * 1.02e-10**3
        Ayy = 0.5 / kappa() * 1.02e-10**3
        Axy = 0.4 / kappa() * 1.02e-10**3
        Axz = 0.1 / kappa() * 1.02e-10**3
        Ayz = 0.2 / kappa() * 1.02e-10**3

        # Set the diffusion parameters.
        self.align_data.set(param='Axx', value=Axx, category='err')
        self.align_data.set(param='Ayy', value=Ayy, category='err')
        self.align_data.set(param='Axy', value=Axy, category='err')
        self.align_data.set(param='Axz', value=Axz, category='err')
        self.align_data.set(param='Ayz', value=Ayz, category='err')

        # Test the set values.
        self.assertEqual(self.align_data.Axx_err, Axx)
        self.assertEqual(self.align_data.Ayy_err, Ayy)
        self.assertEqual(self.align_data.Axy_err, Axy)
        self.assertEqual(self.align_data.Axz_err, Axz)
        self.assertEqual(self.align_data.Ayz_err, Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz_err, Azz)
        self.assertEqual(self.align_data.Axxyy_err, Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.A_err.tostring(), tensor.tostring())


    def test_set_params(self):
        """Test the setting of alignment tensor parameters.

        The following parameters will be set:
            - Axx: -16.6278 Hz
            - Ayy: 6.13037 Hz
            - Axy: 7.65639 Hz
            - Axz: -1.89157 Hz
            - Ayz: 19.2561 Hz
        """

        # The parameter values.
        Axx = -16.6278 / kappa() * 1.02e-10**3
        Ayy = 6.13037 / kappa() * 1.02e-10**3
        Axy = 7.65639 / kappa() * 1.02e-10**3
        Axz = -1.89157 / kappa() * 1.02e-10**3
        Ayz = 19.2561 / kappa() * 1.02e-10**3

        # Set the diffusion parameters.
        self.align_data.set(param='Axx', value=Axx)
        self.align_data.set(param='Ayy', value=Ayy)
        self.align_data.set(param='Axy', value=Axy)
        self.align_data.set(param='Axz', value=Axz)
        self.align_data.set(param='Ayz', value=Ayz)

        # Test the set values.
        self.assertEqual(self.align_data.Axx, Axx)
        self.assertEqual(self.align_data.Ayy, Ayy)
        self.assertEqual(self.align_data.Axy, Axy)
        self.assertEqual(self.align_data.Axz, Axz)
        self.assertEqual(self.align_data.Ayz, Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz, Azz)
        self.assertEqual(self.align_data.Axxyy, Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.A.tostring(), tensor.tostring())


    def test_set_sim(self):
        """Test the setting of Monte Carlo simulation alignment tensor parameters.

        Firstly the following parameters will be appended to empty lists:
            - Axx: -16.6278 Hz
            - Ayy: 6.13037 Hz
            - Axy: 7.65639 Hz
            - Axz: -1.89157 Hz
            - Ayz: 19.2561 Hz

        These MC sim values will then be explicity overwritten by setting the first elements of the
        lists to:
            - Axx: 0.3 Hz
            - Ayy: 0.5 Hz
            - Axy: 0.4 Hz
            - Axz: 0.1 Hz
            - Ayz: 0.2 Hz
        """

        # Set the number of MC sims.
        self.align_data.set_sim_num(1)

        # Append the initial values.
        self.align_data.set(param='Axx', value=-16.6278 / kappa() * 1.02e-10**3, category='sim', sim_index=0)
        self.align_data.set(param='Ayy', value=6.13037 / kappa() * 1.02e-10**3, category='sim', sim_index=0)
        self.align_data.set(param='Axy', value=7.65639 / kappa() * 1.02e-10**3, category='sim', sim_index=0)
        self.align_data.set(param='Axz', value=-1.89157 / kappa() * 1.02e-10**3, category='sim', sim_index=0)
        self.align_data.set(param='Ayz', value=19.2561 / kappa() * 1.02e-10**3, category='sim', sim_index=0)

        # The new MC sim parameter values.
        Axx = 0.3 / kappa() * 1.02e-10**3
        Ayy = 0.5 / kappa() * 1.02e-10**3
        Axy = 0.4 / kappa() * 1.02e-10**3
        Axz = 0.1 / kappa() * 1.02e-10**3
        Ayz = 0.2 / kappa() * 1.02e-10**3

        # Set the MC sim parameter values (overwriting the initial values).
        self.align_data.set(param='Axx', value=Axx, category='sim', sim_index=0)
        self.align_data.set(param='Ayy', value=Ayy, category='sim', sim_index=0)
        self.align_data.set(param='Axy', value=Axy, category='sim', sim_index=0)
        self.align_data.set(param='Axz', value=Axz, category='sim', sim_index=0)
        self.align_data.set(param='Ayz', value=Ayz, category='sim', sim_index=0)

        # Test the set values.
        self.assertEqual(self.align_data.Axx_sim[0], Axx)
        self.assertEqual(self.align_data.Ayy_sim[0], Ayy)
        self.assertEqual(self.align_data.Axy_sim[0], Axy)
        self.assertEqual(self.align_data.Axz_sim[0], Axz)
        self.assertEqual(self.align_data.Ayz_sim[0], Ayz)

        # Calculate the diffusion tensor objects.
        Azz, Axxyy, tensor = self.calc_objects(Axx, Ayy, Axy, Axz, Ayz)

        # Test the automatically created values.
        self.assertEqual(self.align_data.Azz_sim[0], Azz)
        self.assertEqual(self.align_data.Axxyy_sim[0], Axxyy)

        # Test the matrices.
        self.assertEqual(self.align_data.A_sim[0].tostring(), tensor.tostring())


    def test_set_Axx(self):
        """Test the setting of the Axx parameter."""

        # Set the Axx value to 0.0001.
        self.align_data.set(param='Axx', value=0.0001)

        # Test that the Axx parameter has been set correctly.
        self.assertTrue(hasattr(self.align_data, 'Axx'))
        self.assertEqual(self.align_data.Axx, 0.0001)
