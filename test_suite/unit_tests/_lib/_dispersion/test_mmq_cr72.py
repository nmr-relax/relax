###############################################################################
#                                                                             #
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

# Python module imports.
from numpy import array, float64, int16, pi, zeros
from unittest import TestCase

# relax module imports.
from lib.dispersion.mmq_cr72 import r2eff_mmq_cr72


class Test_mmq_cr72(TestCase):
    """Unit tests for the lib.dispersion.mmq_cr72 relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # Default parameter values.
        self.r20 = 2.0
        self.pA = 0.95
        self.dw = 2.0
        self.dwH = 0.5
        self.kex = 1000.0

        # Required data structures.
        self.num_points = 7
        self.ncyc = array([2, 4, 8, 10, 20, 40])
        relax_times = 0.04
        self.cpmg_frqs = self.ncyc / relax_times
        self.inv_relax_times = 1.0 / relax_times
        self.tau_cpmg = 0.25 / self.cpmg_frqs
        self.R2eff = zeros(self.num_points, float64)

        # The spin Larmor frequencies.
        self.sfrq = 200. * 1E6


    def calc_r2eff(self):
        """Calculate and check the R2eff values."""

        # Parameter conversions.
        k_AB, k_BA, pB, dw_frq, dwH_frq = self.param_conversion(pA=self.pA, kex=self.kex, dw=self.dw, dwH=self.dwH, sfrq=self.sfrq)

        # Calculate the R2eff values.
        r2eff_mmq_cr72(r20=self.r20, pA=self.pA, pB=pB, dw=dw_frq, dwH=dwH_frq, kex=self.kex, k_AB=k_AB, k_BA=k_BA, cpmg_frqs=self.cpmg_frqs, inv_tcpmg=self.inv_relax_times, tcp=self.tau_cpmg, back_calc=self.R2eff, num_points=self.num_points, power=self.ncyc)

        # Check all R2eff values.
        for i in range(self.num_points):
            self.assertAlmostEqual(self.R2eff[i], self.r20)


    def param_conversion(self, pA=None, kex=None, dw=None, dwH=None, sfrq=None):
        """Convert the parameters.

        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @keyword dw:    The chemical exchange difference between states A and B in ppm.
        @type dw:       float
        @keyword dwH:   The proton chemical exchange difference between states A and B in ppm.
        @type dwH:      float
        @keyword sfrq:  The spin Larmor frequencies in Hz.
        @type sfrq:     float
        @return:        The parameters {k_AB, k_BA, pB, dw_frq}.
        @rtype:         tuple of float
        """

        # Calculate pB.
        pB = 1.0 - pA

        # Exchange rates.
        k_BA = pA * kex
        k_AB = pB * kex

        # Calculate spin Larmor frequencies in 2pi.
        frqs = sfrq * 2 * pi

        # Convert dw from ppm to rad/s.
        dw_frq = dw * frqs / 1.e6

        # Convert dwH from ppm to rad/s.
        dwH_frq = dwH * frqs / 1.e6

        # Return all values.
        return k_AB, k_BA, pB, dw_frq, dwH_frq


    def test_mmq_cr72_no_rex1(self):
        """Test the r2eff_mmq_cr72() function for no exchange when dw = 0.0 and dwH = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.dwH = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_mmq_cr72_no_rex2(self):
        """Test the r2eff_mmq_cr72() function for no exchange when pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_mmq_cr72_no_rex3(self):
        """Test the r2eff_mmq_cr72() function for no exchange when kex = 0.0."""

        # Parameter reset.
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_mmq_cr72_no_rex4(self):
        """Test the r2eff_mmq_cr72() function for no exchange when dw = 0.0, dwH = 0.0 and pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0
        self.dw = 0.0
        self.dwH = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_mmq_cr72_no_rex5(self):
        """Test the r2eff_mmq_cr72() function for no exchange when dw = 0.0, dwH = 0.0 and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.dwH = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_mmq_cr72_no_rex6(self):
        """Test the r2eff_mmq_cr72() function for no exchange when pA = 1.0 and kex = 0.0."""

        # Parameter reset.
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_mmq_cr72_no_rex7(self):
        """Test the r2eff_mmq_cr72() function for no exchange when dw = 0.0, dwH = 0.0, pA = 1.0, and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.dwH = 0.0
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_mmq_cr72_no_rex8(self):
        """Test the r2eff_mmq_cr72() function for no exchange when kex = 1e5."""

        # Parameter reset.
        self.kex = 1e5

        # Calculate and check the R2eff values.
        self.calc_r2eff()


