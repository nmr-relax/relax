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
from math import pi


# Planck's constant.
h = 6.62606876 * 1e-34

# Dirac's constant.
h_bar = h / (2.0 * pi)

# The magnetic constant or the permeability of vacuum.
mu0 = 4.0 * pi * 1e-7

# The 15N CSA in the NH bond (default value).
N15_CSA = -172 * 1e-6

# The length of the NH bond (default value).
NH_BOND_LENGTH = 1.02 * 1e-10


# The 13C gyromagnetic ratio.
g13C = 6.728 * 1e7

# The 1H gyromagnetic ratio.
g1H = 26.7522212 * 1e7

# The 15N gyromagnetic ratio.
g15N = -2.7126 * 1e7

# The 17O gyromagnetic ratio.
g17O = -3.628 * 1e7

# The 31P gyromagnetic ratio.
g31P = 10.841 * 1e7
