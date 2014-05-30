###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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

# Python module imports.
from numpy import array, float64, int16, pi, zeros
from unittest import TestCase

# relax module imports.
from lib.dispersion.m61b import r1rho_M61b


class Test_m61b(TestCase):
    """Unit tests for the lib.dispersion.m61b relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # The R1rho_prime parameter value (R1rho with no exchange).
        self.r1rho_prime = 2.5
        # Population of ground state.
        self.pA = 0.95
        # The chemical exchange difference between states A and B in ppm.
        self.dw = 0.5
        self.kex = 1000.0
        # The R1 relaxation rates.
        self.r1 = 1.0
        # The spin-lock field strengths in Hertz.
        self.spin_lock_nu1 = array([ 1000., 1500., 2000., 2500., 3000., 3500., 4000., 4500., 5000., 5500., 6000.])
        # The rotating frame tilt angles for each dispersion point.
        self.theta = array([1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966, 1.5707963267948966])

        # The spin Larmor frequencies.
        self.sfrq = 599.8908617*1E6

        # Required data structures.
        self.num_points = 11
        self.R1rho = zeros(self.num_points, float64)


    def calc_r1rho(self):
        """Calculate and check the R1rho values."""

        # Parameter conversions.
        phi_ex_scaled, dw_frq, spin_lock_omega1_squared = self.param_conversion(pA=self.pA, dw=self.dw, sfrq=self.sfrq, spin_lock_nu1=self.spin_lock_nu1)

        # Calculate the R1rho values.
        R1rho = r1rho_M61b(r1rho_prime=self.r1rho_prime, pA=self.pA, dw=dw_frq, kex=self.kex, spin_lock_fields2=spin_lock_omega1_squared, back_calc=self.R1rho, num_points=self.num_points)


        # Check all R1rho values.
        if self.kex > 1.e5:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R1rho[i], self.r1rho_prime, 2)
        else:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R1rho[i], self.r1rho_prime)


    def param_conversion(self, pA=None, dw=None, sfrq=None, spin_lock_nu1=None):
        """Convert the parameters.

        @keyword pA:            The population of state A.
        @type pA:               float
        @keyword dw:            The chemical exchange difference between states A and B in ppm.
        @type dw:               float
        @keyword sfrq:          The spin Larmor frequencies in Hz.
        @type sfrq:             float
        @keyword spin_lock_nu1: The spin-lock field strengths in Hertz.
        @type spin_lock_nu1:    float
        @return:                The parameters {phi_ex_scaled, dw_frq, spin_lock_omega1_squared}.
        @rtype:                 tuple of float
        """

        # Calculate pB.
        pB = 1.0 - pA

        # Calculate spin Larmor frequencies in 2pi.
        frqs = sfrq * 2 * pi

        # Convert dw from ppm to rad/s.
        dw_frq = dw * frqs / 1.e6

        # The phi_ex parameter value (pA * pB * delta_omega^2).
        phi_ex = pA * pB * (dw / 1.e6)**2

        # Convert phi_ex from ppm^2 to (rad/s)^2.
        phi_ex_scaled = phi_ex * frqs**2

        # The R1rho spin-lock field strengths squared (in rad^2.s^-2).
        spin_lock_omega1_squared = (2. * pi * spin_lock_nu1)**2

        # Return all values.
        return phi_ex_scaled, dw_frq, spin_lock_omega1_squared


    def test_m61b_no_rex1(self):
        """Test the r1rho_m61b() function for no exchange when dw = 0.0."""

        # Parameter reset.
        self.dw = 0.0

        # Calculate and check the R1rho values.
        self.calc_r1rho()


    def test_m61b_no_rex2(self):
        """Test the r1rho_m61b() function for no exchange when pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0

        # Calculate and check the R1rho values.
        self.calc_r1rho()


    def test_m61b_no_rex3(self):
        """Test the r1rho_m61b() function for no exchange when kex = 0.0."""

        # Parameter reset.
        self.kex = 0.0

        # Calculate and check the R1rho values.
        self.calc_r1rho()


    def test_m61b_no_rex4(self):
        """Test the r1rho_m61b() function for no exchange when dw = 0.0 and pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0
        self.dw = 0.0

        # Calculate and check the R1rho values.
        self.calc_r1rho()


    def test_m61b_no_rex5(self):
        """Test the r1rho_m61b() function for no exchange when dw = 0.0 and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R1rho values.
        self.calc_r1rho()


    def test_m61b_no_rex6(self):
        """Test the r1rho_m61b() function for no exchange when pA = 1.0 and kex = 0.0."""

        # Parameter reset.
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R1rho values.
        self.calc_r1rho()


    def test_m61b_no_rex7(self):
        """Test the r1rho_m61b() function for no exchange when dw = 0.0, pA = 1.0, and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R1rho values.
        self.calc_r1rho()


    def test_m61b_no_rex8(self):
        """Test the r1rho_m61b() function for no exchange when kex = 1e20."""

        # Parameter reset.
        self.kex = 1e20

        # Calculate and check the R2eff values.
        self.calc_r1rho()
