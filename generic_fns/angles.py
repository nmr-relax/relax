###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007 Edward d'Auvergne                             #
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
from math import acos, pi, sin
from Numeric import dot

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoTensorError




class Angles:
    def __init__(self, relax):
        """Class containing the functions relating to angles."""

        self.relax = relax


    def angles(self, run):
        """Function for calculating the angle defining the XH vector in the diffusion frame."""

        # Test if the run exists.
        if not run in relax_data_store.run_names:
            raise RelaxNoPipeError, run

        # Test if the PDB file has been loaded.
        if not relax_data_store.pdb.has_key(run):
            raise RelaxNoPdbError, run

        # Test if sequence data is loaded.
        if not relax_data_store.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test if the diffusion tensor data is loaded.
        if not relax_data_store.diff.has_key(run):
            raise RelaxNoTensorError, run

        # Arguments.
        self.run = run

        # Sphere.
        if relax_data_store.diff[self.run].type == 'sphere':
            return

        # Spheroid.
        elif relax_data_store.diff[self.run].type == 'spheroid':
            self.spheroid_frame()

        # Ellipsoid.
        elif relax_data_store.diff[self.run].type == 'ellipsoid':
            raise RelaxError, "No coded yet."


    def ellipsoid_frame(self):
        """Function for calculating the spherical angles of the XH vector in the ellipsoid frame."""

        # Get the unit vectors Dx, Dy, and Dz of the diffusion tensor axes.
        Dx, Dy, Dz = self.relax.generic.diffusion_tensor.unit_axes()

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Test if the vector exists.
            if not hasattr(relax_data_store.res[self.run][i], 'xh_vect'):
                print "No angles could be calculated for residue '" + `relax_data_store.res[self.run][i].num` + " " + relax_data_store.res[self.run][i].name + "'."
                continue

            # dz and dx direction cosines.
            dz = dot(Dz, relax_data_store.res[self.run][i].xh_vect)
            dx = dot(Dx, relax_data_store.res[self.run][i].xh_vect)

            # Calculate the polar angle theta.
            relax_data_store.res[self.run][i].theta = acos(dz)

            # Calculate the azimuthal angle phi.
            relax_data_store.res[self.run][i].phi = acos(dx / sin(relax_data_store.res[self.run][i].theta))


    def spheroid_frame(self):
        """Function for calculating the angle alpha of the XH vector within the spheroid frame."""

        # Get the unit vector Dpar of the diffusion tensor axis.
        Dpar = self.relax.generic.diffusion_tensor.unit_axes()

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Test if the vector exists.
            if not hasattr(relax_data_store.res[self.run][i], 'xh_vect'):
                print "No angles could be calculated for residue '" + `relax_data_store.res[self.run][i].num` + " " + relax_data_store.res[self.run][i].name + "'."
                continue

            # Calculate alpha.
            relax_data_store.res[self.run][i].alpha = acos(dot(Dpar, relax_data_store.res[self.run][i].xh_vect))


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
