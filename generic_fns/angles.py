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

from math import acos, pi
from Numeric import dot


class Angles:
    def __init__(self, relax):
        """Class containing the function to calculate the XH vector from the loaded structure."""

        self.relax = relax


    def angles(self, run):
        """Function for calculating the XH vector from the loaded structure."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if the PDB file has been loaded.
        if not self.relax.data.pdb.has_key(run):
            raise RelaxPdbError, run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the diffusion tensor data is loaded.
        if not self.relax.data.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Arguments.
        self.run = run

        # Isotropic diffusion.
        if self.relax.data.diff[self.run].type == 'iso':
            return

        # Axially symmetric diffusion.
        elif self.relax.data.diff[self.run].type == 'axial':
            self.axial()

        # Fully anisotropic diffusion.
        elif self.relax.data.diff[self.run].type == 'aniso':
            raise RelaxError, "No coded yet."


    def axial(self):
        """Function for calculating the angle alpha

        The angle alpha is between the XH vector and the main axis of the axially symmetric
        diffusion tensor.
        """

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Test if the vector has been calculated.
            if not hasattr(self.relax.data.res[self.run][i], 'xh_unit'):
                print "No angles could be calculated for residue '" + `self.relax.data.res[self.run][i].num` + " " + self.relax.data.res[self.run][i].name + "'."
                continue

            # Calculate alpha.
            self.relax.data.res[self.run][i].alpha = acos(dot(self.relax.data.diff[self.run].axis_unit, self.relax.data.res[self.run][i].xh_unit))

            # Print out.
            print `self.relax.data.res[self.run][i].num` + " " + self.relax.data.res[self.run][i].name + ":  alpha = " + `360.0 * self.relax.data.res[self.run][i].alpha / (2.0 * pi)` + " deg."


    def wrap_angles(self, angle, lower, upper):
        """Convert the given angle to be between the lower and upper values."""

        while 1:
            if angle > upper:
                angle = angle - upper
            elif angle < lower:
                angle = angle + upper
            else:
                break

        return angle
