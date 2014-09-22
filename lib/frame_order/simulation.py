###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Module for simulating the frame order motions."""

# Python module imports.
from numpy import eye, float64
import sys

# relax module imports.
from lib.errors import RelaxError


def brownian(file=None, model=None, structure=None, parameters={}, pivot=None, step_size=2.0, snapshot=10, total=1000):
    """Pseudo-Brownian dynamics simulation of the frame order motions.

    @keyword file:          The opened and writable file object to place the snapshots into.
    @type file:             str
    @keyword structure:     The internal structural object containing the domain to simulate as a single model.
    @type structure:        lib.structure.internal.object.Internal instance
    @keyword model:         The frame order model to simulate.
    @type model:            str
    @keyword parameters:    The dictionary of model parameter values.  The key is the parameter name and the value is the value.
    @type parameters:       dict of float
    @keyword pivot:         The pivot point of the frame order motions.
    @type pivot:            numpy rank-1, 3D float64 array
    @keyword step_size:     The rotation will be of a random direction but with this fixed angle.  The value is in degrees.
    @type step_size:        float
    @keyword snapshot:      The number of steps in the simulation when snapshots will be taken.
    @type snapshot:         int
    @keyword total:         The total number of snapshots to take before stopping the simulation.
    @type total:            int
    """

    # Check the structural object.
    if structure.num_models() > 1:
        raise RelaxError("Only a single model is supported.")

    # Set the model number.
    structure.set_model(model_orig=None, model_new=1)

    # The initial state.
    state = eye(3, dtype=float64)

    # Initialise the rotation matrix.
    R = eye(3, dtype=float64)

    # Printout.
    print("\nRunning the simulation:")

    # Simulate.
    current_snapshot = 1
    step = 1
    while 1:
        # End the simulation.
        if current_snapshot == total:
            print("\nEnd of simulation.")
            break

        # Take a snapshot.
        if step == snapshot:
            # Progress.
            sys.stdout.write('.')
            sys.stdout.flush()

            # Increment the snapshot number.
            current_snapshot += 1

            # Copy the original structural data.
            structure.add_model(model=current_snapshot, coords_from=1)

            # Rotate the model.
            structure.rotate(R=R, origin=pivot, model=current_snapshot, atom_id=None)

            # Reset the step counter.
            step = 0

        # Increment.
        step += 1

    # Save the result.
    structure.write_pdb(file=file)
