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
from numpy import array, float64, zeros

# relax module imports.
from lib.errors import RelaxError
from specific_analyses.frame_order.data import pivot_fixed
from specific_analyses.frame_order.variables import MODEL_DOUBLE_ROTOR, MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_LIST_FREE_ROTORS, MODEL_LIST_ISO_CONE, MODEL_LIST_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE, MODEL_ROTOR


def assemble_param_vector(sim_index=None, unset_fail=False):
    """Assemble and return the parameter vector.

    @keyword sim_index:     The Monte Carlo simulation index.
    @type sim_index:        int
    @keyword unset_fail:    A flag which if True will cause a RelaxError to be raised if the parameter is not set yet.
    @type unset_fail:       bool
    @return:                The parameter vector.
    @rtype:                 numpy rank-1 array
    """

    # Initialise.
    param_vect = []

    # Parameter name extension.
    ext = ''
    if sim_index != None:
        ext = '_sim'

    # Loop over all model parameters.
    for param_name in cdp.params:
        # Add the extension.
        param_name += ext

        # The parameter does not exist yet.
        if not hasattr(cdp, param_name):
            if unset_fail:
                raise RelaxError("The parameter '%s' has not been set." % param_name)
            else:
                param_vect.append(None)
                continue

        # Get the object.
        obj = getattr(cdp, param_name)

        # Add it to the parameter vector.
        if sim_index == None:
            param_vect.append(obj)
        else:
            param_vect.append(obj[sim_index])

    # Return as a numpy array.
    return array(param_vect, float64)


def assemble_scaling_matrix(scaling=True):
    """Create and return the scaling matrix.

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

    # Return the matrix.
    return scaling_matrix


def linear_constraints(scaling_matrix=None):
    """Create the linear constraint matrices A and b.

    Standard notation
    =================

    The parameter constraints for the motional amplitude parameters are::

        0 <= theta <= pi,
        0 <= theta_x <= theta_y <= pi,
        -0.125 <= S <= 1,
        0 <= sigma_max <= pi,

    The pivot point and average domain position parameter constraints are::

        -999 <= pivot_x <= 999
        -999 <= pivot_y <= 999
        -999 <= pivot_z <= 999
        -500 <= ave_pos_x <= 500
        -500 <= ave_pos_y <= 500
        -500 <= ave_pos_y <= 500
    
    These are necessary to allow for valid PDB representations to be created.  The eigenframe parameters are unconstrained.


    Matrix notation
    ===============

    In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter values, and b is a vector of scalars, these inequality constraints are::

        | 1  0  0  0  0 |                        |   0    |
        |               |                        |        |
        |-1  0  0  0  0 |                        |  -pi   |
        |               |                        |        |
        | 0  1  0  0  0 |                        |   0    |
        |               |                        |        |
        | 0 -1  0  0  0 |     |   theta   |      |  -pi   |
        |               |     |           |      |        |
        | 0 -1  1  0  0 |     |  theta_x  |      |   0    |
        |               |     |           |      |        |
        | 0  0  1  0  0 |  .  |  theta_y  |  >=  |   0    |
        |               |     |           |      |        |
        | 0  0 -1  0  0 |     |    S      |      |  -pi   |
        |               |     |           |      |        |
        | 0  0  0  1  0 |     | sigma_max |      | -0.125 |
        |               |                        |        |
        | 0  0  0 -1  0 |                        |  -1    |
        |               |                        |        |
        | 0  0  0  0  1 |                        |   0    |
        |               |                        |        |
        | 0  0  0  0 -1 |                        |  -pi   |

    The pivot and average position constraints in the A.x >= b notation are::

        | 1  0  0  0  0  0 |                        | -999.0 |
        |                  |                        |        |
        |-1  0  0  0  0  0 |                        | -999.0 |
        |                  |                        |        |
        | 0  1  0  0  0  0 |                        | -999.0 |
        |                  |                        |        |
        | 0 -1  0  0  0  0 |     |  pivot_x  |      | -999.0 |
        |                  |     |           |      |        |
        | 0  0  1  0  0  0 |     |  pivot_y  |      | -999.0 |
        |                  |     |           |      |        |
        | 0  0 -1  0  0  0 |     |  pivot_z  |      | -999.0 |
        |                  |  .  |           |  >=  |        |
        | 0  0  0  1  0  0 |     | ave_pos_x |      | -500.0 |
        |                  |     |           |      |        |
        | 0  0  0 -1  0  0 |     | ave_pos_y |      | -500.0 |
        |                  |     |           |      |        |
        | 0  0  0  0  1  0 |     | ave_pos_z |      | -500.0 |
        |                  |                        |        |
        | 0  0  0  0 -1  0 |                        | -500.0 |
        |                  |                        |        |
        | 0  0  0  0  0  1 |                        | -500.0 |
        |                  |                        |        |
        | 0  0  0  0  0 -1 |                        | -500.0 |


    @keyword scaling_matrix:    The diagonal, square scaling matrix.
    @type scaling_matrix:       numpy rank-2 square matrix
    @return:                    The matrices A and b.
    @rtype:                     numpy rank-2 NxM array, numpy rank-1 N array
    """

    # Initialisation (0..j..m).
    A = []
    b = []
    n = param_num()
    zero_array = zeros(n, float64)
    i = 0
    j = 0

    # Loop over the parameters of the model.
    for i in range(n):
        # The pivot parameters.
        if cdp.params[i] in ['pivot_x', 'pivot_y', 'pivot_z']:
            # -999 <= pivot_i <= 999.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(-999.0 / scaling_matrix[i, i])
            b.append(-999.0 / scaling_matrix[i, i])
            j = j + 2

        # The average domain translation parameters.
        if cdp.params[i] in ['ave_pos_x', 'ave_pos_y', 'ave_pos_z']:
            # -500 <= ave_pos_i <= 500.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(-500.0 / scaling_matrix[i, i])
            b.append(-500.0 / scaling_matrix[i, i])
            j = j + 2

        # The cone opening angles and sigma_max.
        if cdp.params[i] in ['cone_theta', 'cone_theta_x', 'cone_theta_y', 'cone_sigma_max']:
            # 0 <= theta <= pi.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(0.0)
            b.append(-pi / scaling_matrix[i, i])
            j = j + 2

            # The pseudo-ellipse restriction (theta_x <= theta_y).
            if cdp.params[i] == 'cone_theta_y':
                for m in range(n):
                    if cdp.params[m] == 'cone_theta_x':
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j][m] = -1.0
                        b.append(0.0)
                        j = j + 1


        # The order parameter.
        if cdp.params[i] == 'cone_s1':
            # -0.125 <= S <= 1.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(-0.125 / scaling_matrix[i, i])
            b.append(-1 / scaling_matrix[i, i])
            j = j + 2

    # Convert to numpy data structures.
    A = array(A, float64)
    b = array(b, float64)

    # No constraints are present.
    if len(A) == 0:
        A = None
        b = None

    # Return the constraint objects.
    return A, b


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

    # Printout.
    print("Reinitialising the list of model parameters:")

    # Re-initialise the list of model parameters.
    cdp.params = []

    # The pivot parameters.
    print("    - pivot parameters.")
    if not pivot_fixed():
        cdp.params.append('pivot_x')
        cdp.params.append('pivot_y')
        cdp.params.append('pivot_z')

    # The 2nd pivot point parameters - the minimum inter rotor axis distance.
    if cdp.model in [MODEL_DOUBLE_ROTOR]:
        cdp.params.append('pivot_disp')

    # The average domain position translation parameters.
    print("    - average domain position.")
    cdp.params.append('ave_pos_x')
    cdp.params.append('ave_pos_y')
    cdp.params.append('ave_pos_z')

    # The tensor rotation, or average domain position.
    if cdp.model not in MODEL_LIST_FREE_ROTORS:
        cdp.params.append('ave_pos_alpha')
    cdp.params.append('ave_pos_beta')
    cdp.params.append('ave_pos_gamma')

    # Frame order eigenframe - the full frame.
    print("    - frame order eigenframe.")
    if cdp.model in MODEL_LIST_PSEUDO_ELLIPSE + [MODEL_DOUBLE_ROTOR]:
        cdp.params.append('eigen_alpha')
        cdp.params.append('eigen_beta')
        cdp.params.append('eigen_gamma')

    # Frame order eigenframe - the isotropic cone axis.
    if cdp.model in MODEL_LIST_ISO_CONE:
        cdp.params.append('axis_theta')
        cdp.params.append('axis_phi')

    # Frame order eigenframe - the rotor axis alpha angle.
    if cdp.model in [MODEL_ROTOR, MODEL_FREE_ROTOR]:
        cdp.params.append('axis_alpha')

    # Cone parameters - pseudo-elliptic cone parameters.
    print("    - cone opening half-angles.")
    if cdp.model in MODEL_LIST_PSEUDO_ELLIPSE:
        cdp.params.append('cone_theta_x')
        cdp.params.append('cone_theta_y')

    # Cone parameters - single isotropic angle or order parameter.
    if cdp.model in [MODEL_ISO_CONE, MODEL_ISO_CONE_TORSIONLESS]:
        cdp.params.append('cone_theta')
    if cdp.model in [MODEL_ISO_CONE_FREE_ROTOR]:
        cdp.params.append('cone_s1')

    # Cone parameters - torsion angle.
    print("    - cone torsion half-angles.")
    if cdp.model in [MODEL_DOUBLE_ROTOR, MODEL_ROTOR, MODEL_ISO_CONE, MODEL_PSEUDO_ELLIPSE]:
        cdp.params.append('cone_sigma_max')

    # Cone parameters - 2nd torsion angle.
    if cdp.model in [MODEL_DOUBLE_ROTOR]:
        cdp.params.append('cone_sigma_max_2')
