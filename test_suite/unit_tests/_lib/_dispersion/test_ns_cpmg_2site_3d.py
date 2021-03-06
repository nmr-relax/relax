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
from numpy import array, float64, ones, pi, rollaxis, zeros
from unittest import TestCase

# relax module imports.
from lib.dispersion.ns_cpmg_2site_3d import r2eff_ns_cpmg_2site_3D
from lib.dispersion.ns_matrices import r180x_3d


class Test_ns_cpmg_2site_3d(TestCase):
    """Unit tests for the lib.dispersion.ns_cpmg_2site_3D relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # Default parameter values.
        self.r20a = 2.0
        self.r20b = 3.0
        self.pA = 0.95
        self.dw = 2.0
        self.kex = 1000.0

        # Required data structures.
        # The 3D rotation matrix for an imperfect X-axis pi-pulse.
        self.r180x = r180x_3d()

        self.num_points = 7
        self.ncyc = array([2, 4, 8, 10, 20, 40, 500])
        relax_times = 0.04
        cpmg_frqs = self.ncyc / relax_times
        self.inv_relax_times = 1.0 / relax_times
        self.tau_cpmg = 0.25 / cpmg_frqs

        self.array_shape = [1, 1, 1, 1, self.num_points]
        self.R2eff = zeros(self.num_points, float64) * ones(self.array_shape)

        # The spin Larmor frequencies.
        self.sfrq = 200. * 1E6

        # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        M0_0 = zeros( [1, 1, 1, 1, 1, 7, 1], float64)
        M0_0[:, :, :, :, :, 0, 0] = 0.5
        self.M0 = M0_0
        # Transpose M0, to prepare for dot operation. Roll the last axis one back, corresponds to a transpose for the outer two axis.
        self.M0_T = rollaxis(self.M0, 6, 5)


    def calc_r2eff(self):
        """Calculate and check the R2eff values."""

        # Parameter conversions.
        k_AB, k_BA, pB, dw_frq = self.param_conversion(pA=self.pA, kex=self.kex, dw=self.dw, sfrq=self.sfrq)

        a = ones(self.array_shape)
        b = ones([1, 1, 1, 1])

        # Calculate the R2eff values.
        r2eff_ns_cpmg_2site_3D(r180x=self.r180x, M0=self.M0, M0_T=self.M0_T, r20a=self.r20a*a, r20b=self.r20b*a, pA=self.pA, dw=dw_frq*a, dw_orig=dw_frq*a, kex=self.kex, inv_tcpmg=self.inv_relax_times*a, tcp=self.tau_cpmg*a, back_calc=self.R2eff, num_points=self.num_points*b, power=self.ncyc*a)

        if self.kex >= 1.e5:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R2eff[0][0][0][0][i], self.r20a, 5)
        else:
            for i in range(self.num_points):
                self.assertAlmostEqual(self.R2eff[0][0][0][0][i], self.r20a)


    def param_conversion(self, pA=None, kex=None, dw=None, sfrq=None):
        """Convert the parameters.

        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @keyword dw:    The chemical exchange difference between states A and B in ppm.
        @type dw:       float
        @keyword sfrq:  The spin Larmor frequencies in Hz.
        @type sfrq:     float
        @keyword M0:    Vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        @type M0:       numpy float64, rank-1, 7D array
        @return:        The parameters {k_AB, k_BA, pB, dw_frq, M0}.
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

        # Return all values.
        return k_AB, k_BA, pB, dw_frq


    def test_ns_cpmg_2site_3D_no_rex1(self):
        """Test the r2eff_ns_cpmg_2site_3D() function for no exchange when dw = 0.0."""

        # Parameter reset.
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_3D_no_rex2(self):
        """Test the r2eff_ns_cpmg_2site_3D() function for no exchange when pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_3D_no_rex3(self):
        """Test the r2eff_ns_cpmg_2site_3D() function for no exchange when kex = 0.0."""

        # Parameter reset.
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_3D_no_rex4(self):
        """Test the r2eff_ns_cpmg_2site_3D() function for no exchange when dw = 0.0 and pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_3D_no_rex5(self):
        """Test the r2eff_ns_cpmg_2site_3D() function for no exchange when dw = 0.0 and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_3D_no_rex6(self):
        """Test the r2eff_ns_cpmg_2site_3D() function for no exchange when pA = 1.0 and kex = 0.0."""

        # Parameter reset.
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_ns_cpmg_2site_3D_no_rex7(self):
        """Test the r2eff_ns_cpmg_2site_3D() function for no exchange when dw = 0.0, pA = 1.0, and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()

