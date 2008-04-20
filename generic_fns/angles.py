###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007-2008 Edward d'Auvergne                        #
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
from math import acos, sin
from numpy import dot
from warnings import warn

# relax module imports.
from data import Data as relax_data_store
from generic_fns import pipes
from generic_fns.selection import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoTensorError
from relax_warnings import RelaxWarning


def angle_diff_frame():
    """Function for calculating the angle defining the XH vector in the diffusion frame."""

    # Test if the current data pipe exists.
    pipes.test(relax_data_store.current_pipe)

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the diffusion tensor data is loaded.
    if not hasattr(cdp, 'diff_tensor'):
        raise RelaxNoTensorError, 'diffusion'

    # Sphere.
    if cdp.diff_tensor.type == 'sphere':
        return

    # Spheroid.
    elif cdp.diff_tensor.type == 'spheroid':
        spheroid_frame()

    # Ellipsoid.
    elif cdp.diff_tensor.type == 'ellipsoid':
        raise RelaxError, "No coded yet."


def ellipsoid_frame():
    """Function for calculating the spherical angles of the XH vector in the ellipsoid frame."""

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Get the unit vectors Dx, Dy, and Dz of the diffusion tensor axes.
    Dx, Dy, Dz = diffusion_tensor.unit_axes()

    # Loop over the sequence.
    for i in xrange(len(cdp.mol[0].res)):
        # Test if the vector exists.
        if not hasattr(cdp.mol[0].res[i], 'xh_vect'):
            print "No angles could be calculated for residue '" + `cdp.mol[0].res[i].num` + " " + cdp.mol[0].res[i].name + "'."
            continue

        # dz and dx direction cosines.
        dz = dot(Dz, cdp.mol[0].res[i].xh_vect)
        dx = dot(Dx, cdp.mol[0].res[i].xh_vect)

        # Calculate the polar angle theta.
        cdp.mol[0].res[i].theta = acos(dz)

        # Calculate the azimuthal angle phi.
        cdp.mol[0].res[i].phi = acos(dx / sin(cdp.mol[0].res[i].theta))


def spheroid_frame():
    """Function for calculating the angle alpha of the XH vector within the spheroid frame."""

    # Alias the current data pipe.
    cdp = relax_data_store[relax_data_store.current_pipe]

    # Loop over the sequence.
    for spin in spin_loop():
        # Test if the vector exists.
        if not hasattr(spin, 'xh_vect'):
            warn(RelaxWarning("No angles could be calculated for residue '" + str(spin.num) + " " + str(spin.name) + "'."))
            continue

        # Calculate alpha.
        spin.alpha = acos(dot(cdp.diff_tensor.Dpar_unit, spin.xh_vect))


def wrap_angles(angle, lower, upper):
    """Convert the given angle to be between the lower and upper values."""

    while 1:
        if angle > upper:
            angle = angle - upper
        elif angle < lower:
            angle = angle + upper
        else:
            break

    return angle
