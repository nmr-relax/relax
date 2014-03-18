###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the manipulation of angular information."""

# Python module imports.
from math import acos, sin
from numpy import dot
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError, RelaxNoTensorError
from lib.warnings import RelaxWarning
from pipe_control import pipes
from pipe_control.interatomic import interatomic_loop
from pipe_control.mol_res_spin import exists_mol_res_spin_data, generate_spin_id, spin_loop


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
            spin_id = generate_spin_id(mol_name=mol_name, res_num=res_num, res_name=res_name, spin_num=spin.num, spin_name=spin.name)

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

    # Loop over the interatomic info.
    for interatom in interatomic_loop():
        # Test if the vector exists.
        if not hasattr(interatom, 'vector'):
            # Throw a warning.
            warn(RelaxWarning("No angles could be calculated for the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))

            # Skip the container.
            continue

        # Calculate alpha.
        interatom.alpha = acos(dot(cdp.diff_tensor.Dpar_unit, interatom.vector))
