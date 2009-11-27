###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
# Copyright (C) 2007-2009 Sebastien Morin                                     #
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
from math import cos, pi
from numpy import float64, zeros

# relax module imports.
from ri_comps import calc_fixed_csa, calc_fixed_dip, comp_csa_const_func, comp_dip_const_func


class Consistency:
    def __init__(self, frq=None, gx=None, gh=None, mu0=None, h_bar=None):
        """Consistency tests for data acquired at different magnetic fields.

        These three tests are used to assess the consistency of datasets aquired at different
        magnetic fields. Inconsistency can affect extracted information from experimental data and
        can be caused by variations in temperature, concentration, pH, water suppression, etc. The
        approach is described in Morin & Gagne (2009) JBNMR, 45: 361-372.

        This code calculates three functions for each residue. When comparing datasets from
        different magnetic fields, the value should be the same for each function as these are field
        independent. The J(0) function is the spectral density at the zero frequency and is obtained
        using a reduced spectral density approach (Farrow et al. (1995) JBNMR, 6: 153-162). The
        F_eta and F_R2 functions are the consistency functions proposed by Fushman et al. (1998)
        JACS, 120: 10947-10952.

        To assess the consistency of its datasets, one should first calculate one of those values
        (J(0), F_eta and F_R2, preferentially J(0) as discussed in Morin & Gagne (2009) JBNMR, 45:
        361-372) for each field. Then, the user should compare values obtained for different
        magnetic fields. Comparisons should proceed using correlation plots and histograms, and the
        user could also calculate correlation, skewness and kurtosis coefficients.

        For examples, see Morin & Gagne (2009) JBNMR, 45: 361-372.
        """

        # Initialise the data container.
        self.data = Data()

        # Add the initial data to self.data.
        self.data.gx = gx
        self.data.gh = gh
        self.data.mu0 = mu0
        self.data.h_bar = h_bar

        # The number of frequencies.
        self.data.num_frq = 1

        # Dipolar and CSA data structures.
        self.data.dip_const_fixed = 0.0
        self.data.csa_const_fixed = [0.0]
        self.data.dip_const_func = 0.0
        self.data.csa_const_func = zeros(1, float64)

        # Nuclear frequencies.
        frq = frq * 2 * pi
        frqX = frq * self.data.gx / self.data.gh

        # Calculate the five frequencies which cause R1, R2, and NOE relaxation.
        self.data.frq_list = zeros((1, 5), float64)
        self.data.frq_list[0, 1] = frqX
        self.data.frq_list[0, 2] = frq - frqX
        self.data.frq_list[0, 3] = frq
        self.data.frq_list[0, 4] = frq + frqX
        self.data.frq_sqrd_list = self.data.frq_list ** 2


    def calc_sigma_noe(self, noe, r1):
        """Function for calculating the sigma NOE value."""

        return (noe - 1.0) * r1 * self.data.gx / self.data.gh


    def func(self, orientation=None, tc=None, r=None, csa=None, r1=None, r2=None, noe=None):
        """Function for calculating the three consistency testing values.

        Three values are returned, J(0), F_eta and F_R2.
        """

        # Calculate the fixed component of the dipolar and CSA constants.
        calc_fixed_dip(self.data)
        calc_fixed_csa(self.data)

        # Calculate the dipolar and CSA constants.
        comp_dip_const_func(self.data, r)
        comp_csa_const_func(self.data, csa)

        # Rename the dipolar and CSA constants.
        d = self.data.dip_const_func
        c = self.data.csa_const_func[0]

        # Calculate the sigma NOE value.
        sigma_noe = self.calc_sigma_noe(noe, r1)

        # Calculate J(0).
        j0 = -1.5 / (3.0*d + c) * (0.5*r1 - r2 + 0.6*sigma_noe)

        # Calculate J(wX).
        jwx = 1.0 / (3.0*d + c) * (r1 - 1.4*sigma_noe)

        # Calculate P_2.
        # p_2 is a second rank Legendre polynomial as p_2(x) = 0.5 * (3 * (x ** 2) -1)
        # where x is the cosine of the angle Theta when expressed in radians.
        #
        # Note that the angle Theta (called 'orientation' in relax) is the angle between the 15N-1H
        # vector and the principal axis of the 15N chemical shift tensor.
        p_2 = 0.5 * ((3.0 * (cos(orientation * pi / 180)) ** 2) -1)

        # Calculate eta.
        # eta is the cross-correlation rate between 15N CSA and 15N-1H dipolar interaction. It is
        # expressed here as proposed in Fushman & Cowburn (1998) JACS, 120: 7109-7110.
        eta = ((d * c/3.0) ** 0.5) * (4.0 * j0 + 3.0 * jwx) * p_2

        # Calculate F_eta.
        # F_eta is independent of the magnetic field for residues with local mobility
        f_eta = eta * self.data.gh / (self.data.frq_list[0, 3] * (4.0 + 3.0 / (1 + (self.data.frq_list[0, 1] * tc) ** 2)))

        # Calculate P_HF.
        # P_HF is the contribution to R2 from high frequency motions.
        # P_HF = 0.5 * d * [J(wH-wN) + 6 * J(wH) + 6 * J(wH+wN)].
        # Here, P_HF is described using a reduced spectral density approach.
        p_hf = 1.3 * (self.data.gx / self.data.gh) * (1.0 - noe) * r1

        # Calculate F_R2.
        # F_R2 tests the consistency of the transverse relaxation data.
        f_r2 = (r2 - p_hf) / ((4.0 + 3.0 / (1 + (self.data.frq_list[0, 1] * tc) ** 2)) * (d + c/3.0))

        # Return the three values.
        return j0, f_eta, f_r2


class Data:
    def __init__(self):
        """Empty container for storing data."""
