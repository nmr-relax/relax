###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
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

class Fix:
    def __init__(self, relax):
        """Class containing the function for fixing or allowing parameter values to change."""

        self.relax = relax


    def fix(self, run, param_type, fixed):
        """Function for fixing or allowing parameter values to change."""

        # Diffusion tensor.
        if param_type == 'diff':
            self.relax.data.diff[run].fixed = fixed

        # Unknown.
        else:
            raise RelaxError, "The 'param_type' argument must currently be set to 'diff'."
