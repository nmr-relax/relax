###############################################################################
#                                                                             #
# Copyright (C) 2009-2014 Edward d'Auvergne                                   #
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
"""Module for handling the frame order model parameters."""

# Python module imports.
from math import pi
from numpy import array, float64, identity, ones, zeros

# relax module imports.
from specific_analyses.frame_order.data import base_data_types, pivot_fixed, translation_fixed


def assemble_limit_arrays():
    """Assemble and return the limit vectors.

    @return:    The lower and upper limit vectors.
    @rtype:     numpy rank-1 array, numpy rank-1 array
    """

    # Init.
    lower = zeros(len(cdp.params), float64)
    upper = 2.0*pi * ones(len(cdp.params), float64)

    # Return the arrays.
    return lower, upper


def assemble_param_vector(sim_index=None):
    """Assemble and return the parameter vector.

    @return:            The parameter vector.
    @rtype:             numpy rank-1 array
    @keyword sim_index: The Monte Carlo simulation index.
    @type sim_index:    int
    """

    # Initialise.
    param_vect = []

    # Parameter name extension.
    ext = ''
    if sim_index != None:
        ext = '_sim'

    # Loop over all model parameters.
    for param_name in cdp.params:
        # Get the object.
        obj = getattr(cdp, param_name+ext)

        # Add it to the parameter vector.
        if sim_index == None:
            param_vect.append(obj)
        else:
            param_vect.append(obj[sim_index])

    # Return as a numpy array.
    return array(param_vect, float64)


def assemble_scaling_matrix(data_types=None, scaling=True):
    """Create and return the scaling matrix.

    @keyword data_types:    The base data types used in the optimisation.  This list can contain the elements 'rdc', 'pcs' or 'tensor'.
    @type data_types:       list of str
    @keyword scaling:       If False, then the identity matrix will be returned.
    @type scaling:          bool
    @return:                The square and diagonal scaling matrix.
    @rtype:                 numpy rank-2 array
    """

    # Initialise.
    scaling_matrix = identity(param_num(), float64)

    # Return the identity matrix.
    if not scaling:
        return scaling_matrix

    # The pivot point.
    if not pivot_fixed():
        for i in range(3):
            scaling_matrix[i, i] = 1e2

    # Return the matrix.
    return scaling_matrix


def param_num():
    """Determine the number of parameters in the model.

    @return:    The number of model parameters.
    @rtype:     int
    """

    # Update the model, just in case.
    update_model()

    # Simple parameter list count.
    return len(cdp.params)


def update_model():
    """Update the model parameters as necessary."""

    # Re-initialise the list of model parameters.
    cdp.params = []

    # The pivot parameters.
    if not pivot_fixed():
        cdp.params.append('pivot_x')
        cdp.params.append('pivot_y')
        cdp.params.append('pivot_z')

        # Double rotor.
        if cdp.model == 'double rotor':
            cdp.params.append('pivot_x_2')
            cdp.params.append('pivot_y_2')
            cdp.params.append('pivot_z_2')

    # The average domain position translation parameters.
    if not translation_fixed():
        cdp.params.append('ave_pos_x')
        cdp.params.append('ave_pos_y')
        cdp.params.append('ave_pos_z')

    # The tensor rotation, or average domain position.
    if cdp.model not in ['free rotor', 'iso cone, free rotor']:
        cdp.params.append('ave_pos_alpha')
    cdp.params.append('ave_pos_beta')
    cdp.params.append('ave_pos_gamma')

    # Frame order eigenframe - the full frame.
    if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
        cdp.params.append('eigen_alpha')
        cdp.params.append('eigen_beta')
        cdp.params.append('eigen_gamma')

    # Frame order eigenframe - the isotropic cone axis.
    if cdp.model in ['iso cone', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'double rotor']:
        cdp.params.append('axis_theta')
        cdp.params.append('axis_phi')

    # Frame order eigenframe - the second rotation axis.
    if cdp.model in ['double rotor']:
        cdp.params.append('axis_theta_2')
        cdp.params.append('axis_phi_2')

    # Frame order eigenframe - the rotor axis alpha angle.
    if cdp.model in ['rotor']:
        cdp.params.append('axis_alpha')

    # Cone parameters - pseudo-elliptic cone parameters.
    if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
        cdp.params.append('cone_theta_x')
        cdp.params.append('cone_theta_y')

    # Cone parameters - single isotropic angle or order parameter.
    if cdp.model in ['iso cone', 'iso cone, torsionless']:
        cdp.params.append('cone_theta')
    if cdp.model in ['iso cone, free rotor']:
        cdp.params.append('cone_s1')

    # Cone parameters - torsion angle.
    if cdp.model in ['double rotor', 'rotor', 'line', 'iso cone', 'pseudo-ellipse']:
        cdp.params.append('cone_sigma_max')

    # Cone parameters - 2nd torsion angle.
    if cdp.model in ['double rotor']:
        cdp.params.append('cone_sigma_max_2')

    # Initialise the parameters in the current data pipe.
    for param in cdp.params:
        if not param in ['pivot_x', 'pivot_y', 'pivot_z', 'pivot_x_2', 'pivot_y_2', 'pivot_z_2'] and not hasattr(cdp, param):
            setattr(cdp, param, 0.0)
