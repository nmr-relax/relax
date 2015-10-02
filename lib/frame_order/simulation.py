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
from math import cos, pi, sin, sqrt
from numpy import dot, eye, float64, transpose, zeros
import sys

# relax module imports.
from lib.errors import RelaxError
from lib.geometry.angles import wrap_angles
from lib.geometry.rotations import axis_angle_to_R, R_to_tilt_torsion, tilt_torsion_to_R
from lib.geometry.vectors import random_unit_vector


def brownian(file=None, model=None, structure=None, parameters={}, eigenframe=None, pivot=None, atom_id=None, step_size=2.0, snapshot=10, total=1000):
    """Pseudo-Brownian dynamics simulation of the frame order motions.

    @keyword file:          The opened and writable file object to place the snapshots into.
    @type file:             str
    @keyword structure:     The internal structural object containing the domain to simulate as a single model.
    @type structure:        lib.structure.internal.object.Internal instance
    @keyword model:         The frame order model to simulate.
    @type model:            str
    @keyword parameters:    The dictionary of model parameter values.  The key is the parameter name and the value is the value.
    @type parameters:       dict of float
    @keyword eigenframe:    The full 3D eigenframe of the frame order motions.
    @type eigenframe:       numpy rank-2, 3D float64 array
    @keyword pivot:         The pivot point of the frame order motions.
    @type pivot:            numpy rank-1, 3D float64 array
    @keyword atom_id:       The atom ID string for the atoms in the structure to rotate - i.e. the moving domain.
    @type atom_id:          None or str
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

    # Initialise the rotation matrix data structures.
    vector = zeros(3, float64)
    R = eye(3, dtype=float64)
    step_size = step_size / 360.0 * 2.0 * pi

    # The maximum cone opening angles (isotropic cones).
    theta_max = None
    if 'cone_theta_max' in parameters:
        theta_max = parameters['cone_theta_max']

    # The maximum cone opening angles (isotropic cones).
    theta_x = None
    theta_y = None
    if 'cone_theta_x' in parameters:
        theta_x = parameters['cone_theta_x']
        theta_y = parameters['cone_theta_y']

    # The maximum torsion angle.
    sigma_max = None
    if 'cone_sigma_max' in parameters:
        sigma_max = parameters['cone_sigma_max']
    elif 'free rotor' in model:
        sigma_max = pi

    # The second torsion angle.
    sigma_max_2 = None
    if 'cone_sigma_max_2' in parameters:
        sigma_max_2 = parameters['cone_sigma_max_2']

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

        # The random vector.
        random_unit_vector(vector)

        # The rotation matrix.
        axis_angle_to_R(vector, step_size, R)

        # Shift the current state.
        state = dot(R, state)

        # Rotation in the eigenframe.
        R_eigen = dot(transpose(eigenframe), dot(state, eigenframe))

        # The angles.
        phi, theta, sigma = R_to_tilt_torsion(R_eigen)
        sigma = wrap_angles(sigma, -pi, pi)

        # Determine theta_max.
        if theta_x != None:
            theta_max = 1.0 / sqrt((cos(phi) / theta_x)**2 + (sin(phi) / theta_y)**2)

        # Set the cone opening angle to the maximum if outside of the limit.
        if theta_max != None:
            if theta > theta_max:
                theta = theta_max

        # No tilt component.
        else:
            theta = 0.0
            phi = 0.0

        # Set the torsion angle to the maximum if outside of the limits.
        if sigma_max != None:
            if sigma > sigma_max:
                sigma = sigma_max
            elif sigma < -sigma_max:
                sigma = -sigma_max
        else:
            sigma = 0.0

        # Reconstruct the rotation matrix, in the eigenframe, without sigma.
        tilt_torsion_to_R(phi, theta, sigma, R_eigen)

        # Rotate back out of the eigenframe.
        state = dot(eigenframe, dot(R_eigen, transpose(eigenframe)))

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
            structure.rotate(R=state, origin=pivot, model=current_snapshot, atom_id=atom_id)

            # Reset the step counter.
            step = 0

        # Increment.
        step += 1

    # Save the result.
    structure.write_pdb(file=file)
