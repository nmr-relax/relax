###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007-2010 Edward d'Auvergne                        #
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

# Module docstring.
"""Module for the manipulation of angular information."""

# Python module imports.
from math import acos, pi, sin
from numpy import dot
from warnings import warn

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id, spin_loop
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoTensorError
from relax_warnings import RelaxWarning


def angle_diff_frame():
    """Function for calculating the angle defining the XH vector in the diffusion frame."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Test if the diffusion tensor data is loaded.
    if not hasattr(cdp, 'diff_tensor'):
        raise RelaxNoTensorError('diffusion')

    # Sphere.
    if cdp.diff_tensor.type == 'sphere':
        return

    # Spheroid.
    elif cdp.diff_tensor.type == 'spheroid':
        spheroid_frame()

    # Ellipsoid.
    elif cdp.diff_tensor.type == 'ellipsoid':
        raise RelaxError("No coded yet.")


def ellipsoid_frame():
    """Calculate the spherical angles of the bond vector in the ellipsoid frame."""

    # Get the unit vectors Dx, Dy, and Dz of the diffusion tensor axes.
    Dx, Dy, Dz = diffusion_tensor.unit_axes()

    # Spin loop.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Test if the vector exists.
        if not hasattr(spin, 'xh_vect'):
            # Get the spin id string.
            spin_id = generate_spin_id(mol_name, res_num, res_name, spin.num, spin.name)

            # Throw a warning.
            warn(RelaxWarning("No angles could be calculated for the spin " + repr(spin_id) + "."))

            # Skip the spin.
            continue

        # dz and dx direction cosines.
        dz = dot(Dz, spin.xh_vect)
        dx = dot(Dx, spin.xh_vect)

        # Calculate the polar angle theta.
        spin.theta = acos(dz)

        # Calculate the azimuthal angle phi.
        spin.phi = acos(dx / sin(spin.theta))


def spheroid_frame():
    """Function for calculating the angle alpha of the XH vector within the spheroid frame."""

    # Loop over the sequence.
    for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
        # Test if the vector exists.
        if not hasattr(spin, 'xh_vect'):
            # Get the spin id string.
            spin_id = generate_spin_id(mol_name, res_num, res_name, spin.num, spin.name)

            # Throw a warning.
            warn(RelaxWarning("No angles could be calculated for the spin " + repr(spin_id) + "."))

            # Skip the spin.
            continue

        # Calculate alpha.
        spin.alpha = acos(dot(cdp.diff_tensor.Dpar_unit, spin.xh_vect))


def wrap_angles(angle, lower, upper, window=2*pi):
    """Convert the given angle to be between the lower and upper values.

    @param angle:   The starting angle.
    @type angle:    float
    @param lower:   The lower bound.
    @type lower:    float
    @param upper:   The upper bound.
    @type upper:    float
    @param window:  The size of the window where symmetry exists (defaults to 2pi).
    @type window:   float
    @return:        The wrapped angle.
    @rtype:         float
    """

    # Check the bounds and window.
    if window - (upper - lower) > 1e-7:
        raise RelaxError, "The lower and upper bounds [%s, %s] do not match the window size of %s." % (lower, upper, window)

    # Keep wrapping until the angle is within the limits.
    while True:
        # The angle is too big.
        if angle > upper:
            angle = angle - window

        # The angle is too small.
        elif angle < lower:
            angle = angle + window

        # Inside the window, so stop wrapping.
        else:
            break

    # Return the wrapped angle.
    return angle
