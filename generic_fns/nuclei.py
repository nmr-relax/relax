###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

from re import match


class Nuclei:
    def __init__(self, relax):
        """Class containing the function to set the gyromagnetic ratio of the heteronucleus."""

        self.relax = relax


    def nuclei(self, heteronuc):
        """Function for setting the gyromagnetic ratio of the heteronucleus."""

        # Nitrogen.
        if match('[Nn]', heteronuc):
            self.relax.data.gx = -2.7126e7

        # Carbon
        elif match('[Cc]', heteronuc):
            self.relax.data.gx = 6.728e7

        # Oxygen.
        elif match('[Oo]', heteronuc):
            self.relax.data.gx = -3.628e7

        # Phosphate.
        elif match('[Pp]', heteronuc):
            self.relax.data.gx = 1.0841e8

        # Incorrect arguement.
        else:
            raise RelaxInvalidError, ('heteronucleus', heteronuc)

        # Set the proton gyromagnetic ratio.
        #self.relax.data.gh = 26.7522e7
        self.relax.data.gh = 26.7522212e7


        # Calculate the ratio of the gyromagnetic ratios.
        self.relax.data.g_ratio = self.relax.data.gh / self.relax.data.gx
