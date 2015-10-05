###############################################################################
#                                                                             #
# Copyright (C) 2014-2015 Edward d'Auvergne                                   #
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
from warnings import warn

# relax module imports.
from lib.errors import RelaxError
from lib.warnings import RelaxWarning
from lib.frame_order.variables import MODEL_DOUBLE_ROTOR
from lib.geometry.angles import wrap_angles
from lib.geometry.rotations import axis_angle_to_R, R_random_hypersphere, R_to_tilt_torsion, tilt_torsion_to_R
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
    @keyword pivot:         The list of pivot points of the frame order motions.
    @type pivot:            numpy rank-2 (N, 3) float64 array
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

    # Generate the internal structural selection object.
    selection = structure.selection(atom_id)

    # The initial states and motional limits.
    num_states = len(pivot)
    states = zeros((num_states, 3, 3), float64)
    theta_max = []
    sigma_max = []
    for i in range(num_states):
        states[i] = eye(3)
        theta_max.append(None)
        sigma_max.append(None)

    # Initialise the rotation matrix data structures.
    vector = zeros(3, float64)
    R = eye(3, dtype=float64)
    step_size = step_size / 360.0 * 2.0 * pi

    # Axis permutations.
    perm = [None]
    if model == MODEL_DOUBLE_ROTOR:
        perm = [[2, 0, 1], [1, 2, 0]]
        perm_rev = [[1, 2, 0], [2, 0, 1]]

    # The maximum cone opening angles (isotropic cones).
    if 'cone_theta' in parameters:
        theta_max[0] = parameters['cone_theta']

    # The maximum cone opening angles (isotropic cones).
    theta_x = None
    theta_y = None
    if 'cone_theta_x' in parameters:
        theta_x = parameters['cone_theta_x']
        theta_y = parameters['cone_theta_y']

    # The maximum torsion angle.
    if 'cone_sigma_max' in parameters:
        sigma_max[0] = parameters['cone_sigma_max']
    elif 'free rotor' in model:
        sigma_max[0] = pi

    # The second torsion angle.
    if 'cone_sigma_max_2' in parameters:
        sigma_max[1] = parameters['cone_sigma_max_2']

    # Printout.
    print("\nRunning the simulation:")

    # Simulate.
    current_snapshot = 1
    step = 1
    while True:
        # End the simulation.
        if current_snapshot == total:
            print("\nEnd of simulation.")
            break

        # Loop over each state, or motional mode.
        for i in range(num_states):
            # The random vector.
            random_unit_vector(vector)

            # The rotation matrix.
            axis_angle_to_R(vector, step_size, R)

            # Shift the current state.
            states[i] = dot(R, states[i])

            # Rotation in the eigenframe.
            R_eigen = dot(transpose(eigenframe), dot(states[i], eigenframe))

            # Axis permutation to shift each rotation axis to Z.
            if perm[i] != None:
                for j in range(3):
                    R_eigen[:, j] = R_eigen[perm[i], j]
                for j in range(3):
                    R_eigen[j, :] = R_eigen[j, perm[i]]

            # The angles.
            phi, theta, sigma = R_to_tilt_torsion(R_eigen)
            sigma = wrap_angles(sigma, -pi, pi)

            # Determine theta_max for the pseudo-ellipse models.
            if theta_x != None:
                theta_max[i] = 1.0 / sqrt((cos(phi) / theta_x)**2 + (sin(phi) / theta_y)**2)

            # Set the cone opening angle to the maximum if outside of the limit.
            if theta_max[i] != None:
                if theta > theta_max[i]:
                    theta = theta_max[i]

            # No tilt component.
            else:
                theta = 0.0
                phi = 0.0

            # Set the torsion angle to the maximum if outside of the limits.
            if sigma_max[i] != None:
                if sigma > sigma_max[i]:
                    sigma = sigma_max[i]
                elif sigma < -sigma_max[i]:
                    sigma = -sigma_max[i]
            else:
                sigma = 0.0

            # Reconstruct the rotation matrix, in the eigenframe, without sigma.
            tilt_torsion_to_R(phi, theta, sigma, R_eigen)

            # Reverse axis permutation to shift each rotation z-axis back.
            if perm[i] != None:
                for j in range(3):
                    R_eigen[:, j] = R_eigen[perm_rev[i], j]
                for j in range(3):
                    R_eigen[j, :] = R_eigen[j, perm_rev[i]]

            # Rotate back out of the eigenframe.
            states[i] = dot(eigenframe, dot(R_eigen, transpose(eigenframe)))

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
            for i in range(num_states):
                structure.rotate(R=states[i], origin=pivot[i], model=current_snapshot, selection=selection)

            # Reset the step counter.
            step = 0

        # Increment.
        step += 1

    # Save the result.
    structure.write_pdb(file=file)


def uniform_distribution(file=None, model=None, structure=None, parameters={}, eigenframe=None, pivot=None, atom_id=None, total=1000, max_rotations=100000):
    """Uniform distribution of the frame order motions.

    @keyword file:          The opened and writable file object to place the PDB models of the distribution into.
    @type file:             str
    @keyword structure:     The internal structural object containing the domain to distribute as a single model.
    @type structure:        lib.structure.internal.object.Internal instance
    @keyword model:         The frame order model to distribute.
    @type model:            str
    @keyword parameters:    The dictionary of model parameter values.  The key is the parameter name and the value is the value.
    @type parameters:       dict of float
    @keyword eigenframe:    The full 3D eigenframe of the frame order motions.
    @type eigenframe:       numpy rank-2, 3D float64 array
    @keyword pivot:         The list of pivot points of the frame order motions.
    @type pivot:            numpy rank-2 (N, 3) float64 array
    @keyword atom_id:       The atom ID string for the atoms in the structure to rotate - i.e. the moving domain.
    @type atom_id:          None or str
    @keyword total:         The total number of states in the distribution.
    @type total:            int
    @keyword max_rotations: The maximum number of rotations to generate the distribution from.  This prevents an execution for an infinite amount of time when a frame order amplitude parameter is close to zero so that the subset of all rotations within the distribution is close to zero.
    @type max_rotations:    int
    """

    # Check the structural object.
    if structure.num_models() > 1:
        raise RelaxError("Only a single model is supported.")

    # Set the model number.
    structure.set_model(model_orig=None, model_new=1)

    # Generate the internal structural selection object.
    selection = structure.selection(atom_id)

    # The initial states and motional limits.
    num_states = len(pivot)
    states = zeros((num_states, 3, 3), float64)
    theta_max = []
    sigma_max = []
    for i in range(num_states):
        states[i] = eye(3)
        theta_max.append(None)
        sigma_max.append(None)

    # Initialise the rotation matrix data structures.
    R = eye(3, dtype=float64)

    # Axis permutations.
    perm = [None]
    if model == MODEL_DOUBLE_ROTOR:
        perm = [[2, 0, 1], [1, 2, 0]]
        perm_rev = [[1, 2, 0], [2, 0, 1]]

    # The maximum cone opening angles (isotropic cones).
    if 'cone_theta' in parameters:
        theta_max[0] = parameters['cone_theta']

    # The maximum cone opening angles (isotropic cones).
    theta_x = None
    theta_y = None
    if 'cone_theta_x' in parameters:
        theta_x = parameters['cone_theta_x']
        theta_y = parameters['cone_theta_y']

    # The maximum torsion angle.
    if 'cone_sigma_max' in parameters:
        sigma_max[0] = parameters['cone_sigma_max']
    elif 'free rotor' in model:
        sigma_max[0] = pi

    # The second torsion angle.
    if 'cone_sigma_max_2' in parameters:
        sigma_max[1] = parameters['cone_sigma_max_2']

    # Printout.
    print("\nGenerating the distribution:")

    # Distribution.
    current_state = 1
    num = -1
    while True:
        # The total number of rotations.
        num += 1

        # End.
        if current_state == total:
            break
        if num >= max_rotations:
            sys.stdout.write('\n')
            warn(RelaxWarning("Maximum number of rotations encountered - the distribution only contains %i states." % current_state))
            break

        # Loop over each state, or motional mode.
        inside = True
        for i in range(num_states):
            # The random rotation matrix.
            R_random_hypersphere(R)

            # Shift the current state.
            states[i] = dot(R, states[i])

            # Rotation in the eigenframe.
            R_eigen = dot(transpose(eigenframe), dot(states[i], eigenframe))

            # Axis permutation to shift each rotation axis to Z.
            if perm[i] != None:
                for j in range(3):
                    R_eigen[:, j] = R_eigen[perm[i], j]
                for j in range(3):
                    R_eigen[j, :] = R_eigen[j, perm[i]]

            # The angles.
            phi, theta, sigma = R_to_tilt_torsion(R_eigen)
            sigma = wrap_angles(sigma, -pi, pi)

            # Determine theta_max for the pseudo-ellipse models.
            if theta_x != None:
                theta_max[i] = 1.0 / sqrt((cos(phi) / theta_x)**2 + (sin(phi) / theta_y)**2)

            # The cone opening angle is outside of the limit.
            if theta_max[i] != None:
                if theta > theta_max[i]:
                    inside = False

            # No tilt component.
            else:
                theta = 0.0
                phi = 0.0

            # The torsion angle is outside of the limits.
            if sigma_max[i] != None:
                if sigma > sigma_max[i]:
                    inside = False
                elif sigma < -sigma_max[i]:
                    inside = False
            else:
                sigma = 0.0

            # Reconstruct the rotation matrix, in the eigenframe, without sigma.
            tilt_torsion_to_R(phi, theta, sigma, R_eigen)

            # Reverse axis permutation to shift each rotation z-axis back.
            if perm[i] != None:
                for j in range(3):
                    R_eigen[:, j] = R_eigen[perm_rev[i], j]
                for j in range(3):
                    R_eigen[j, :] = R_eigen[j, perm_rev[i]]

            # Rotate back out of the eigenframe.
            states[i] = dot(eigenframe, dot(R_eigen, transpose(eigenframe)))

        # The state is outside of the distribution.
        if not inside:
            continue

        # Progress.
        sys.stdout.write('.')
        sys.stdout.flush()

        # Increment the snapshot number.
        current_state += 1

        # Copy the original structural data.
        structure.add_model(model=current_state, coords_from=1)

        # Rotate the model.
        for i in range(num_states):
            structure.rotate(R=states[i], origin=pivot[i], model=current_state, selection=selection)

    # Save the result.
    structure.write_pdb(file=file)
