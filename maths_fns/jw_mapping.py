###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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
from math import pi
from numpy import float64, zeros

# relax module imports.
from maths_fns.ri_comps import calc_fixed_csa, calc_fixed_dip, comp_csa_const_func, comp_dip_const_func


class Mapping:
    def __init__(self, frq=None, gx=None, gh=None, mu0=None, h_bar=None):
        """Reduced spectral density mapping."""

        # Initialise the data container.
        self.data = Data()

        # Add the initial data to self.data
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


    def func(self, r=None, csa=None, r1=None, r2=None, noe=None):
        """Function for calculating the three spectal density values.

        Three values are returned, J(0), J(wX), and J(wH) (or J(0.87wH)).
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

        # Calculate J(wH).
        jwh = sigma_noe / (5.0*d)

        # Return the three values.
        return j0, jwx, jwh


class Data:
    def __init__(self):
        """Empty container for storing data."""
