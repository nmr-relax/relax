###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the macro for setting up the diffusion tensor."""

        self.relax = relax


    def data_names(self):
        """Function for returning a list of names of data structures associated with the sequence."""

        names = [ 'diff_type',
                  'diff_params' ]

        return names


    def set(self, run=None, diff=None, params=None):
        """Function for setting up the diffusion tensor."""

        # Initialise the data structures.
        if not hasattr(self.relax.data, 'diff_type'):
            self.relax.data.diff_type = {}
        if not hasattr(self.relax.data, 'diff_params'):
            self.relax.data.diff_params = {}

        # Setup the diffusion type.
        self.relax.data.diff_type[run] = diff

        # Setup the parameter values.
        if diff == 'iso':
            self.relax.data.diff_params[run] = [params]
        else:
            self.relax.data.diff_params[run] = params
