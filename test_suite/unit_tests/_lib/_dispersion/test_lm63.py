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
from numpy import array, float64, ones, pi, zeros
from unittest import TestCase

# relax module imports.
from lib.dispersion.lm63 import r2eff_LM63


class Test_lm63(TestCase):
    """Unit tests for the lib.dispersion.lm63 relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # Default parameter values.
        self.r20 = 2.0
        self.pA = 0.95
        self.dw = 0.5
        self.kex = 100.0

        # The spin Larmor frequencies.
        self.sfrq = 599.8908617*1E6

        # Required data structures.
        self.num_points = 3
        self.cpmg_frqs = array([2.5, 1.25, 0.83], float64)
        self.R2eff = zeros(self.num_points, float64)


    def calc_r2eff(self):
        """Calculate and check the R2eff values."""

        # Parameter conversions.
        phi_ex_scaled = self.param_conversion(pA=self.pA, dw=self.dw, sfrq=self.sfrq)

        a = ones([self.num_points])

        # Calculate the R2eff values.
        R2eff = r2eff_LM63(r20=self.r20*a, phi_ex=phi_ex_scaled*a, kex=self.kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.R2eff)

        # Check all R2eff values.
        if self.kex > 1.e5:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R2eff[i], self.r20, 2)
        else:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R2eff[i], self.r20)


    def param_conversion(self, pA=None, dw=None, sfrq=None):
        """Convert the parameters.

        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword dw:    The chemical exchange difference between states A and B in ppm.
        @type dw:       float
        @keyword sfrq:  The spin Larmor frequencies in Hz.
        @type sfrq:     float
        @return:        The parameters phi_ex_scaled
        @rtype:         float
        """

        # Calculate pB.
        pB = 1.0 - pA

        # Calculate spin Larmor frequencies in 2pi.
        frqs = sfrq * 2 * pi

        # The phi_ex parameter value (pA * pB * delta_omega^2).
        phi_ex = pA * pB * (dw / 1.e6)**2

        # Convert phi_ex from ppm^2 to (rad/s)^2.
        phi_ex_scaled = phi_ex * frqs**2

        # Return all values.
        return phi_ex_scaled


    def test_lm63_no_rex1(self):
        """Test the r2eff_lm63() function for no exchange when dw = 0.0."""

        # Parameter reset.
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_lm63_no_rex2(self):
        """Test the r2eff_lm63() function for no exchange when pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_lm63_no_rex3(self):
        """Test the r2eff_lm63() function for no exchange when kex = 0.0."""

        # Parameter reset.
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_lm63_no_rex4(self):
        """Test the r2eff_lm63() function for no exchange when dw = 0.0 and pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_lm63_no_rex5(self):
        """Test the r2eff_lm63() function for no exchange when dw = 0.0 and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_lm63_no_rex6(self):
        """Test the r2eff_lm63() function for no exchange when pA = 1.0 and kex = 0.0."""

        # Parameter reset.
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_lm63_no_rex7(self):
        """Test the r2eff_lm63() function for no exchange when dw = 0.0, pA = 1.0, and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_lm63_no_rex8(self):
        """Test the r2eff_lm63() function for no exchange when kex = 1e20."""

        # Parameter reset.
        self.kex = 1e20

        # Calculate and check the R2eff values.
        self.calc_r2eff()
