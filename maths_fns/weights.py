###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

from Numeric import Float64, array


def calc_ci_iso(data):
    """Weight equations for isotropic diffusion.

    c0 = 1
    """

    data.ci[data.i][0] = 1.0


def calc_ci_axial(data):
    """Weight equations for axially symmetric diffusion.

    The equations are:

        c0 = 1/4 (3delta**2 - 1)
        c1 = 3delta**2 (1 - delta**2)
        c2 = 3/4 (1 - delta**2)**2

    where delta is the dot product of the unit bond vector and the unit vector along Dpar.
    """

    data.ci[data.i][0] = 0.25 * (3.0 * data.delta**2 - 1.0)
    data.ci[data.i][1] = 3.0 * data.delta**2 * (1.0 - data.delta**2)
    data.ci[data.i][2] = 0.75 * (1.0 - data.delta**2)**2
