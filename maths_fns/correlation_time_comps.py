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


# Axially symmetric global correlation time components.
#######################################################

def calc_axial_ti_comps(diff_data):
    """Components of the diffusional correlation times.

    The components are:

        five_Dper_plus_Dpar = 5Dper + Dpar
        Dper_plus_two_Dpar = Dper + 2Dpar
    """

    diff_data.five_Dper_plus_Dpar = 5.0 * diff_data.params[0] + diff_data.params[1]
    diff_data.Dper_plus_two_Dpar = diff_data.params[0] + 2.0 * diff_data.params[1]



# Axially symmetric global correlation time gradient components.
################################################################

def calc_axial_dti_comps(diff_data):
    """Components of the diffusional correlation time gradients.

    The components are:

        five_Dper_plus_Dpar_sqrd = (5Dper + Dpar)**2
        Dper_plus_two_Dpar_sqrd = (Dper + 2Dpar)**2
    """

    diff_data.five_Dper_plus_Dpar_sqrd = diff_data.five_Dper_plus_Dpar ** 2
    diff_data.Dper_plus_two_Dpar_sqrd = diff_data.Dper_plus_two_Dpar ** 2



# Axially symmetric global correlation time Hessian components.
###############################################################

def calc_axial_d2ti_comps(diff_data):
    """Components of the diffusional correlation time Hessians.

    The components are:

        five_Dper_plus_Dpar_cubed = (5Dper + Dpar)**3
        Dper_plus_two_Dpar_cubed = (Dper + 2Dpar)**3
    """

    diff_data.five_Dper_plus_Dpar_cubed = diff_data.five_Dper_plus_Dpar ** 3
    diff_data.Dper_plus_two_Dpar_cubed = diff_data.Dper_plus_two_Dpar ** 3
