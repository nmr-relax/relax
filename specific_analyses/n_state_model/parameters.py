###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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

# Package docstring.
"""Module for handling the parameters of the N-state model or structural ensemble analysis."""

# Python module imports.
from numpy import array, float64, identity, zeros
from re import search
from warnings import warn

# relax module imports.
from lib.errors import RelaxNoModelError
from lib.warnings import RelaxWarning
from pipe_control import align_tensor, pipes
from specific_analyses.n_state_model.data import base_data_types, opt_tensor, opt_uses_align_data


def assemble_param_vector(sim_index=None):
    """Assemble all the parameters of the model into a single array.

    @param sim_index:       The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:        None or int
    @return:                The parameter vector used for optimisation.
    @rtype:                 numpy array
    """

    # Test if the model is selected.
    if not hasattr(cdp, 'model') or not isinstance(cdp.model, str):
        raise RelaxNoModelError

    # Determine the data type.
    data_types = base_data_types()

    # Initialise the parameter vector.
    param_vector = []

    # A RDC or PCS data type requires the alignment tensors to be at the start of the parameter vector (unless the tensors are fixed).
    if opt_uses_align_data():
        for i in range(len(cdp.align_tensors)):
            # Skip non-optimised tensors.
            if not opt_tensor(cdp.align_tensors[i]):
                continue

            # Add the parameters.
            param_vector = param_vector + list(cdp.align_tensors[i].A_5D)

    # Monte Carlo simulation data structures.
    if sim_index != None:
        # Populations.
        if cdp.model in ['2-domain', 'population']:
            probs = cdp.probs_sim[sim_index]

        # Euler angles.
        if cdp.model == '2-domain':
            alpha = cdp.alpha_sim[sim_index]
            beta = cdp.beta_sim[sim_index]
            gamma = cdp.gamma_sim[sim_index]

    # Normal data structures.
    else:
        # Populations.
        if cdp.model in ['2-domain', 'population']:
            probs = cdp.probs

        # Euler angles.
        if cdp.model == '2-domain':
            alpha = cdp.alpha
            beta = cdp.beta
            gamma = cdp.gamma

    # The probabilities (exclude that of state N).
    if cdp.model in ['2-domain', 'population']:
        param_vector = param_vector + probs[0:-1]

    # The Euler angles.
    if cdp.model == '2-domain':
        for i in range(cdp.N):
            param_vector.append(alpha[i])
            param_vector.append(beta[i])
            param_vector.append(gamma[i])

    # The paramagnetic centre.
    if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
        if not hasattr(cdp, 'paramagnetic_centre'):
            for i in range(3):
                param_vector.append(0.0)
        elif sim_index != None:
            if cdp.paramagnetic_centre_sim[sim_index] == None:
                for i in range(3):
                    param_vector.append(0.0)
            else:
                for i in range(3):
                    param_vector.append(cdp.paramagnetic_centre_sim[sim_index][i])
        else:
            for i in range(3):
                param_vector.append(cdp.paramagnetic_centre[i])

    # Convert all None values to zero (to avoid conversion to NaN).
    for i in range(len(param_vector)):
        if param_vector[i] == None:
            param_vector[i] = 0.0

    # Return a numpy arrary.
    return array(param_vector, float64)


def assemble_scaling_matrix(data_types=None, scaling=True):
    """Create and return the scaling matrix.

    @keyword data_types:    The base data types used in the optimisation.  This list can contain
                            the elements 'rdc', 'pcs' or 'tensor'.
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

    # Starting point of the populations.
    pop_start = 0

    # Loop over the alignments.
    tensor_num = 0
    for i in range(len(cdp.align_tensors)):
        # Skip non-optimised tensors.
        if not opt_tensor(cdp.align_tensors[i]):
            continue

        # Add the 5 alignment parameters.
        pop_start = pop_start + 5

        # The alignment parameters.
        for j in range(5):
            scaling_matrix[5*tensor_num + j, 5*tensor_num + j] = 1.0

        # Increase the tensor number.
        tensor_num += 1

    # Loop over the populations, and set the scaling factor.
    if cdp.model in ['2-domain', 'population']:
        factor = 0.1
        for i in range(pop_start, pop_start + (cdp.N-1)):
            scaling_matrix[i, i] = factor

    # The paramagnetic centre.
    if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
        for i in range(-3, 0):
            scaling_matrix[i, i] = 1e2

    # Return the matrix.
    return scaling_matrix


def disassemble_param_vector(param_vector=None, data_types=None, sim_index=None):
    """Disassemble the parameter vector and place the values into the relevant variables.

    For the 2-domain N-state model, the parameters are stored in the probability and Euler angle data structures.  For the population N-state model, only the probabilities are stored.  If RDCs are present and alignment tensors are optimised, then these are stored as well.

    @keyword data_types:    The base data types used in the optimisation.  This list can contain the elements 'rdc', 'pcs' or 'tensor'.
    @type data_types:       list of str
    @keyword param_vector:  The parameter vector returned from optimisation.
    @type param_vector:     numpy array
    @keyword sim_index:     The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:        None or int
    """

    # Test if the model is selected.
    if not hasattr(cdp, 'model') or not isinstance(cdp.model, str):
        raise RelaxNoModelError

    # Unpack and strip off the alignment tensor parameters.
    if ('rdc' in data_types or 'pcs' in data_types) and not align_tensor.all_tensors_fixed():
        # Loop over the alignments, adding the alignment tensor parameters to the tensor data container.
        tensor_num = 0
        for i in range(len(cdp.align_tensors)):
            # Skip non-optimised tensors.
            if not opt_tensor(cdp.align_tensors[i]):
                continue

            # Normal tensors.
            if sim_index == None:
                cdp.align_tensors[i].set(param='Axx', value=param_vector[5*tensor_num])
                cdp.align_tensors[i].set(param='Ayy', value=param_vector[5*tensor_num+1])
                cdp.align_tensors[i].set(param='Axy', value=param_vector[5*tensor_num+2])
                cdp.align_tensors[i].set(param='Axz', value=param_vector[5*tensor_num+3])
                cdp.align_tensors[i].set(param='Ayz', value=param_vector[5*tensor_num+4])

            # Monte Carlo simulated tensors.
            else:
                cdp.align_tensors[i].set(param='Axx', value=param_vector[5*tensor_num], category='sim', sim_index=sim_index)
                cdp.align_tensors[i].set(param='Ayy', value=param_vector[5*tensor_num+1], category='sim', sim_index=sim_index)
                cdp.align_tensors[i].set(param='Axy', value=param_vector[5*tensor_num+2], category='sim', sim_index=sim_index)
                cdp.align_tensors[i].set(param='Axz', value=param_vector[5*tensor_num+3], category='sim', sim_index=sim_index)
                cdp.align_tensors[i].set(param='Ayz', value=param_vector[5*tensor_num+4], category='sim', sim_index=sim_index)

            # Increase the tensor number.
            tensor_num += 1

        # Create a new parameter vector without the tensors.
        param_vector = param_vector[5*tensor_num:]

    # Alias the Monte Carlo simulation data structures.
    if sim_index != None:
        # Populations.
        if cdp.model in ['2-domain', 'population']:
            probs = cdp.probs_sim[sim_index]

        # Euler angles.
        if cdp.model == '2-domain':
            alpha = cdp.alpha_sim[sim_index]
            beta = cdp.beta_sim[sim_index]
            gamma = cdp.gamma_sim[sim_index]

    # Alias the normal data structures.
    else:
        # Populations.
        if cdp.model in ['2-domain', 'population']:
            probs = cdp.probs

        # Euler angles.
        if cdp.model == '2-domain':
            alpha = cdp.alpha
            beta = cdp.beta
            gamma = cdp.gamma

    # Set the probabilities for states 0 to N-1 in the aliased structures.
    if cdp.model in ['2-domain', 'population']:
        for i in range(cdp.N-1):
            probs[i] = param_vector[i]

        # The probability for state N.
        probs[-1] = 1 - sum(probs[0:-1])

    # Set the Euler angles in the aliased structures.
    if cdp.model == '2-domain':
        for i in range(cdp.N):
            alpha[i] = param_vector[cdp.N-1 + 3*i]
            beta[i] = param_vector[cdp.N-1 + 3*i + 1]
            gamma[i] = param_vector[cdp.N-1 + 3*i + 2]

    # The paramagnetic centre.
    if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
        # Create the structure if needed.
        if not hasattr(cdp, 'paramagnetic_centre'):
            cdp.paramagnetic_centre = zeros(3, float64)

        # The position.
        if sim_index == None:
            cdp.paramagnetic_centre[0] = param_vector[-3]
            cdp.paramagnetic_centre[1] = param_vector[-2]
            cdp.paramagnetic_centre[2] = param_vector[-1]

        # Monte Carlo simulated positions.
        else:
            if cdp.paramagnetic_centre_sim[sim_index] == None:
                cdp.paramagnetic_centre_sim[sim_index] = [None, None, None]
            cdp.paramagnetic_centre_sim[sim_index][0] = param_vector[-3]
            cdp.paramagnetic_centre_sim[sim_index][1] = param_vector[-2]
            cdp.paramagnetic_centre_sim[sim_index][2] = param_vector[-1]


def elim_no_prob():
    """Remove all structures or states which have no probability."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the model is setup.
    if not hasattr(cdp, 'model'):
        raise RelaxNoModelError('N-state')

    # Test if there are populations.
    if not hasattr(cdp, 'probs'):
        raise RelaxError("The N-state model populations do not exist.")

    # Create the data structure if needed.
    if not hasattr(cdp, 'select_models'):
        cdp.state_select = [True] * cdp.N

    # Loop over the structures.
    for i in range(len(cdp.N)):
        # No probability.
        if cdp.probs[i] < 1e-5:
            cdp.state_select[i] = False


def linear_constraints(data_types=None, scaling_matrix=None):
    """Function for setting up the linear constraint matrices A and b.

    Standard notation
    =================

    The N-state model constraints are::

        0 <= pc <= 1,

    where p is the probability and c corresponds to state c.


    Matrix notation
    ===============

    In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
    values, and b is a vector of scalars, these inequality constraints are::

        | 1  0  0 |                   |    0    |
        |         |                   |         |
        |-1  0  0 |                   |   -1    |
        |         |                   |         |
        | 0  1  0 |                   |    0    |
        |         |     |  p0  |      |         |
        | 0 -1  0 |     |      |      |   -1    |
        |         |  .  |  p1  |  >=  |         |
        | 0  0  1 |     |      |      |    0    |
        |         |     |  p2  |      |         |
        | 0  0 -1 |                   |   -1    |
        |         |                   |         |
        |-1 -1 -1 |                   |   -1    |
        |         |                   |         |
        | 1  1  1 |                   |    0    |

    This example is for a 4-state model, the last probability pn is not included as this
    parameter does not exist (because the sum of pc is equal to 1).  The Euler angle parameters
    have been excluded here but will be included in the returned A and b objects.  These
    parameters simply add columns of zero to the A matrix and have no effect on b.  The last two
    rows correspond to the inequality::

        0 <= pN <= 1.

    As::
                N-1
                \
        pN = 1 - >  pc,
                /__
                c=1

    then::

        -p1 - p2 - ... - p(N-1) >= -1,

         p1 + p2 + ... + p(N-1) >= 0.


    @keyword data_types:        The base data types used in the optimisation.  This list can
                                contain the elements 'rdc', 'pcs' or 'tensor'.
    @type data_types:           list of str
    @keyword scaling_matrix:    The diagonal scaling matrix.
    @type scaling_matrix:       numpy rank-2 square matrix
    @return:                    The matrices A and b.
    @rtype:                     tuple of len 2 of a numpy rank-2, size NxM matrix and numpy
                                rank-1, size N array
    """

    # Starting point of the populations.
    pop_start = 0
    if ('rdc' in data_types or 'pcs' in data_types) and not align_tensor.all_tensors_fixed():
        # Loop over the alignments.
        for i in range(len(cdp.align_tensors)):
            # Skip non-optimised tensors.
            if not opt_tensor(cdp.align_tensors[i]):
                continue

            # Add 5 parameters.
            pop_start += 5

    # Initialisation (0..j..m).
    A = []
    b = []
    zero_array = zeros(param_num(), float64)
    i = pop_start
    j = 0

    # Probability parameters.
    if cdp.model in ['2-domain', 'population']:
        # Loop over the prob parameters (N - 1, because the sum of pc is 1).
        for k in range(cdp.N - 1):
            # 0 <= pc <= 1.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(0.0)
            b.append(-1.0 / scaling_matrix[i, i])
            j = j + 2

            # Increment i.
            i = i + 1

        # Add the inequalities for pN.
        A.append(zero_array * 0.0)
        A.append(zero_array * 0.0)
        for i in range(pop_start, pop_start+cdp.N-1):
            A[-2][i] = -1.0
            A[-1][i] = 1.0
        b.append(-1.0 / scaling_matrix[i, i])
        b.append(0.0)

    # Convert to numpy data structures.
    A = array(A, float64)
    b = array(b, float64)

    # Return the constraint objects.
    return A, b


def number_of_states(N=None):
    """Set the number of states in the N-state model.

    @param N:   The number of states.
    @type N:    int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Set the value of N.
    cdp.N = N

    # Update the model, if set.
    if hasattr(cdp, 'model'):
        update_model()


def param_model_index(param):
    """Return the N-state model index for the given parameter.

    @param param:   The N-state model parameter.
    @type param:    str
    @return:        The N-state model index.
    @rtype:         str
    """

    # Probability.
    if search('^p[0-9]*$', param):
        return int(param[1:])

    # Alpha Euler angle.
    if search('^alpha', param):
        return int(param[5:])

    # Beta Euler angle.
    if search('^beta', param):
        return int(param[4:])

    # Gamma Euler angle.
    if search('^gamma', param):
        return int(param[5:])

    # Model independent parameter.
    return None


def param_num():
    """Determine the number of parameters in the model.

    @return:    The number of model parameters.
    @rtype:     int
    """

    # Determine the data type.
    data_types = base_data_types()

    # Init.
    num = 0

    # Alignment tensor params.
    if ('rdc' in data_types or 'pcs' in data_types) and not align_tensor.all_tensors_fixed():
        # Loop over the alignments.
        for i in range(len(cdp.align_tensors)):
            # Skip non-optimised tensors.
            if not opt_tensor(cdp.align_tensors[i]):
                continue

            # Add 5 tensor parameters.
            num += 5

    # Populations.
    if cdp.model in ['2-domain', 'population']:
        num = num + (cdp.N - 1)

    # Euler angles.
    if cdp.model == '2-domain':
        num = num + 3*cdp.N

    # The paramagnetic centre.
    if hasattr(cdp, 'paramag_centre_fixed') and not cdp.paramag_centre_fixed:
        num = num + 3

     # Return the param number.
    return num


def ref_domain(ref=None):
    """Set the reference domain for the '2-domain' N-state model.

    @param ref: The reference domain.
    @type ref:  str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the model is setup.
    if not hasattr(cdp, 'model'):
        raise RelaxNoModelError('N-state')

    # Test that the correct model is set.
    if cdp.model != '2-domain':
        raise RelaxError("Setting the reference domain is only possible for the '2-domain' N-state model.")

    # Test if the reference domain exists.
    exists = False
    for tensor_cont in cdp.align_tensors:
        if tensor_cont.domain == ref:
            exists = True
    if not exists:
        raise RelaxError("The reference domain cannot be found within any of the loaded tensors.")

    # Set the reference domain.
    cdp.ref_domain = ref

    # Update the model.
    update_model()


def select_model(model=None):
    """Select the N-state model type.

    @param model:   The N-state model type.  Can be one of '2-domain', 'population', or 'fixed'.
    @type model:    str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if the model name exists.
    if not model in ['2-domain', 'population', 'fixed']:
        raise RelaxError("The model name " + repr(model) + " is invalid.")

    # Test if the model is setup.
    if hasattr(cdp, 'model'):
        warn(RelaxWarning("The N-state model has already been set up.  Switching from model '%s' to '%s'." % (cdp.model, model)))

    # Set the model
    cdp.model = model

    # Initialise the list of model parameters.
    cdp.params = []

    # Update the model.
    update_model()


def update_model():
    """Update the model parameters as necessary."""

    # Initialise the list of model parameters.
    if not hasattr(cdp, 'params'):
        cdp.params = []

    # Determine the number of states (loaded as structural models), if not already set.
    if not hasattr(cdp, 'N'):
        # Set the number.
        if hasattr(cdp, 'structure'):
            cdp.N = cdp.structure.num_models()

        # Otherwise return as the rest cannot be updated without N.
        else:
            return

    # Set up the parameter arrays.
    if not cdp.params:
        # Add the probability or population weight parameters.
        if cdp.model in ['2-domain', 'population']:
            for i in range(cdp.N-1):
                cdp.params.append('p' + repr(i))

        # Add the Euler angle parameters.
        if cdp.model == '2-domain':
            for i in range(cdp.N):
                cdp.params.append('alpha' + repr(i))
                cdp.params.append('beta' + repr(i))
                cdp.params.append('gamma' + repr(i))

    # Initialise the probability and Euler angle arrays.
    if cdp.model in ['2-domain', 'population']:
        if not hasattr(cdp, 'probs'):
            cdp.probs = [None] * cdp.N
    if cdp.model == '2-domain':
        if not hasattr(cdp, 'alpha'):
            cdp.alpha = [None] * cdp.N
        if not hasattr(cdp, 'beta'):
            cdp.beta = [None] * cdp.N
        if not hasattr(cdp, 'gamma'):
            cdp.gamma = [None] * cdp.N

    # Determine the data type.
    data_types = base_data_types()

    # Set up tensors for each alignment.
    if hasattr(cdp, 'align_ids'):
        for id in cdp.align_ids:
            # No tensors initialised.
            if not hasattr(cdp, 'align_tensors'):
                align_tensor.init(tensor=id, align_id=id, params=[0.0, 0.0, 0.0, 0.0, 0.0])

            # Find if the tensor corresponding to the id exists.
            exists = False
            for tensor in cdp.align_tensors:
                if id == tensor.align_id:
                    exists = True

            # Initialise the tensor.
            if not exists:
                align_tensor.init(tensor=id, align_id=id, params=[0.0, 0.0, 0.0, 0.0, 0.0])
