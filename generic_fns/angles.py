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

from math import acos, pi
from Numeric import dot


class Angles:
    def __init__(self, relax):
        """Class containing the function to calculate the XH vector from the loaded structure."""

        self.relax = relax


    def angles(self, run):
        """Function for calculating the XH vector from the loaded structure."""

        # Test if the PDB file has been loaded.
        if not hasattr(self.relax.data, 'pdb'):
            raise RelaxPdbError

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Test if the diffusion tensor data is loaded.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Arguments.
        self.run = run

        # Isotropic diffusion.
        if self.relax.data.diff[run].type == 'iso':
            return

        # Axially symmetric diffusion.
        elif self.relax.data.diff[run].type == 'axial':
            self.axial()

        # Fully anisotropic diffusion.
        elif self.relax.data.diff[run].type == 'aniso':
            raise RelaxError, "No coded yet."


    def axial(self):
        """Function for calculating the angle alpha

        The angle alpha is between the XH vector and the main axis of the axially symmetric
        diffusion tensor.
        """

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Test if the vector has been calculated.
            if not hasattr(self.relax.data.res[i], 'xh_unit'):
                print "No angles could be calculated for residue '" + `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name + "'."
                continue

            # Calculate alpha.
            self.relax.data.res[i].alpha = acos(dot(self.relax.data.diff[self.run].axis_unit, self.relax.data.res[i].xh_unit))

            # Print out.
            print `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name + ":  alpha = " + `360.0 * self.relax.data.res[i].alpha / (2.0 * pi)` + " deg."
