###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""Functions relating to the parameters of the relaxation dispersion models."""

# Python module imports.
from numpy import array, float64, identity, zeros
from re import search

# relax module imports.
from lib.errors import RelaxError
from lib.mathematics import round_to_next_order
from specific_analyses.relax_disp.disp_data import count_frq, loop_frq, loop_frq_point
from specific_analyses.relax_disp.variables import MODEL_R2EFF, MODEL_M61B, VAR_TIME_EXP


def assemble_param_vector(spins=None, key=None, sim_index=None):
    """Assemble the dispersion relaxation dispersion curve fitting parameter vector.

    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @keyword key:           The key for the R2eff and I0 parameters.
    @type key:              str or None
    @keyword sim_index:     The optional MC simulation index.
    @type sim_index:        int
    @return:                An array of the parameter values of the dispersion relaxation model.
    @rtype:                 numpy float array
    """

    # Initialise.
    param_vector = []

    # Loop over the parameters of the cluster.
    for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
        # Spin specific parameters.
        if spin_index != None:
            # Set the simulation value.
            if sim_index != None:
                # Get the simulation structure.
                sim_obj = getattr(spins[spin_index], param_name+'_sim')

                # Frequency specific parameter.
                if frq_index != None:
                    value = sim_obj[sim_index][frq_index]

                # Set the normal value.
                else:
                    value = sim_obj[sim_index]

            # Frequency specific parameter.
            elif frq_index != None:
                obj = getattr(spins[spin_index], param_name)
                if obj == []:
                    value = 0.0
                else:
                    value = obj[frq_index]

            # Set the normal value.
            else:
                value = getattr(spins[spin_index], param_name)

        # Cluster specific parameters - use the parameter value from the first spin.
        else:
            # Set the simulation value.
            if sim_index != None:
                value = getattr(spins[0], param_name+'_sim')[sim_index]

            # Set the normal value.
            else:
                value = getattr(spins[0], param_name)

        # The R2eff model parameters.
        if key != None:
            if not key in value:
                value = 0.0
            else:
                value = value[key]

        # Add to the vector.
        param_vector.append(value)

    # Convert all None values to 0.0.
    for i in range(len(param_vector)):
        if param_vector[i] == None:
            param_vector[i] = 0.0

    # Return a numpy array.
    return array(param_vector, float64)


def assemble_scaling_matrix(spins=None, key=None, scaling=True):
    """Create and return the scaling matrix.

    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @keyword key:           The key for the R2eff and I0 parameters.
    @type key:              str or None
    @keyword scaling:       A flag which if False will cause the identity matrix to be returned.
    @type scaling:          bool
    @return:                The diagonal and square scaling matrix.
    @rtype:                 numpy diagonal matrix
    """

    # Initialise.
    scaling_matrix = identity(param_num(spins=spins), float64)
    i = 0
    param_index = 0

    # No diagonal scaling.
    if not scaling:
        return scaling_matrix

    # Loop over the parameters of the cluster.
    for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
        # Transversal relaxation rate scaling.
        if param_name == 'r2':
            scaling_matrix[param_index, param_index] = 10

        # The pA.pB.dw**2 and pA.dw**2 parameters.
        elif param_name in ['phi_ex', 'padw2']:
            scaling_matrix[param_index, param_index] = 1

        # Chemical shift difference between states A and B scaling.
        elif param_name == 'dw':
            scaling_matrix[param_index, param_index] = 1

        # Transversal relaxation rate scaling.
        elif param_name == 'r2a':
            scaling_matrix[param_index, param_index] = 10

        # The population of state A.
        elif param_name == 'pA':
            scaling_matrix[param_index, param_index] = 1

        # Exchange rate scaling.
        elif param_name in ['kex', 'ka']:
            scaling_matrix[param_index, param_index] = 10000

        # Time of exchange scaling.
        elif param_name == 'tex':
            scaling_matrix[param_index, param_index] = 1e4

    # Return the scaling matrix.
    return scaling_matrix


def disassemble_param_vector(param_vector=None, key=None, spins=None, sim_index=None):
    """Disassemble the parameter vector.

    @keyword param_vector:  The parameter vector.
    @type param_vector:     numpy array
    @keyword key:           The key for the R2eff and I0 parameters.
    @type key:              str or None
    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @keyword sim_index:     The optional MC simulation index.
    @type sim_index:        int
    """

    # Initialise parameters if needed.
    for spin in spins:
        if 'r2' in spin.params:
            if sim_index != None:
                spin.r2_sim[sim_index] = []
                for frq in loop_frq():
                    spin.r2_sim[sim_index].append(None)
            else:
                spin.r2 = []
                for frq in loop_frq():
                    spin.r2.append(None)

    # Loop over the parameters of the cluster.
    for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
        # Spin specific parameters.
        if spin_index != None:
            # Get the object.
            if sim_index != None:
                obj = getattr(spins[spin_index], param_name+'_sim')
            else:
                obj = getattr(spins[spin_index], param_name)

            # Set the simulation value.
            if sim_index != None:
                # Frequency specific parameter.
                if frq_index != None:
                    if key != None:
                        obj[sim_index][frq_index][key] = param_vector[param_index]
                    else:
                        obj[sim_index][frq_index] = param_vector[param_index]

                # Set the normal value.
                else:
                    if key != None:
                        obj[sim_index][key] = param_vector[param_index]
                    else:
                        obj[sim_index] = param_vector[param_index]

            # Frequency specific parameter.
            elif frq_index != None:
                obj = getattr(spins[spin_index], param_name)
                if key != None:
                    obj[frq_index][key] = param_vector[param_index]
                else:
                    obj[frq_index] = param_vector[param_index]

            # Set the normal value.
            else:
                if key != None:
                    obj[key] = param_vector[param_index]
                else:
                    setattr(spins[spin_index], param_name, param_vector[param_index])

        # Cluster specific parameters.
        else:
            # Set the same parameter value for all spins in the cluster.
            for spin in spins:
                # Set the simulation value.
                if sim_index != None:
                    sim_obj = getattr(spin, param_name+'_sim')
                    sim_obj[sim_index] = param_vector[param_index]

                # Set the normal value.
                else:
                    setattr(spin, param_name, param_vector[param_index])


def linear_constraints(spins=None, scaling_matrix=None):
    """Set up the relaxation dispersion curve fitting linear constraint matrices A and b.

    Standard notation
    =================

    The different constraints used within different models are::

        R2 >= 0
        R2 <= -200
        R2A >= 0
        pB <= pA <= 1
        pA >= 0.85 (the skewed condition, pA >> pB)
        phi_ex >= 0
        padw2 >= 0
        dw >= 0
        kex >= 0
        tex >= 0
        kA >= 0


    Matrix notation
    ===============

    In the notation A.x >= b, where A is a matrix of coefficients, x is an array of parameter values, and b is a vector of scalars, these inequality constraints are::

        | 1  0  0 |     |   R2   |      |    0    |
        |         |     |        |      |         |
        |-1  0  0 |     |   R2   |      |  -200   |
        |         |     |        |      |         |
        | 1  0  0 |     |  R2A   |      |    0    |
        |         |     |        |      |         |
        | 1  0  0 |     |   pA   |      |   0.5   |
        |         |     |        |      |         |
        |-1  0  0 |     |   pA   |      |   -1    |
        |         |     |        |      |         |
        | 1  0  0 |     |   pA   |      |   0.85  |
        |         |  .  |        |  >=  |         |
        | 1  0  0 |     | phi_ex |      |    0    |
        |         |     |        |      |         |
        | 1  0  0 |     | padw2  |      |    0    |
        |         |     |        |      |         |
        | 1  0  0 |     |   dw   |      |    0    |
        |         |     |        |      |         |
        | 1  0  0 |     |  kex   |      |    0    |
        |         |     |        |      |         |
        | 1  0  0 |     |  tex   |      |    0    |
        |         |     |        |      |         |
        | 1  0  0 |     |   kA   |      |    0    |


    @keyword spins:             The list of spin data containers for the block.
    @type spins:                list of SpinContainer instances
    @keyword scaling_matrix:    The diagonal, square scaling matrix.
    @type scaling_matrix:       numpy diagonal matrix
    """

    # Initialisation (0..j..m).
    A = []
    b = []
    n = param_num(spins=spins)
    zero_array = zeros(n, float64)
    j = 0

    # Loop over the parameters of the cluster.
    for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
        # Effective transversal relaxation rate.
        if param_name == 'r2eff':
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][param_index] = 1.0
            A[j+1][param_index] = -1.0
            b.append(0.0)
            b.append(-200.0 / scaling_matrix[param_index, param_index])
            j += 2

        # Initial intensity.
        elif param_name == 'i0':
            A.append(zero_array * 0.0)
            A[j][param_index] = 1.0
            b.append(0.0)
            j += 1

        # The transversal relaxation rates (0 <= r2 <= 200).
        elif param_name == 'r2':
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][param_index] = 1.0
            A[j+1][param_index] = -1.0
            b.append(0.0)
            b.append(-200.0 / scaling_matrix[param_index, param_index])
            j += 2

        # The pA.pB.dw**2 and pA.dw**2 parameters (phi_ex >= 0 and padw2 >= 0).
        elif param_name in ['phi_ex', 'padw2']:
            A.append(zero_array * 0.0)
            A[j][param_index] = 1.0
            b.append(0.0)
            j += 1

        # Chemical exchange difference (dw >= 0).
        elif param_name == 'dw':
            A.append(zero_array * 0.0)
            A[j][param_index] = 1.0
            b.append(0.0)
            j += 1

        # The transversal relaxation rates (0 <= r2 <= 200).
        elif param_name == 'r2a':
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][param_index] = 1.0
            A[j+1][param_index] = -1.0
            b.append(0.0)
            b.append(-200.0 / scaling_matrix[param_index, param_index])
            j += 2

        # The population of state A.
        elif param_name == 'pA':
            # First the pA <= 1 constraint
            A.append(zero_array * 0.0)
            A[j][param_index] = -1.0
            b.append(-1.0 / scaling_matrix[param_index, param_index])
            j += 1

            # The skewed condition (pA >> pB).
            if spins[0].model == MODEL_M61B:
                A.append(zero_array * 0.0)
                A[j][param_index] = 1.0
                b.append(0.85 / scaling_matrix[param_index, param_index])
                j += 1

            # Otherwise use the pA >= pB constraint.
            else:
                A.append(zero_array * 0.0)
                A[j][param_index] = 1.0
                b.append(0.5 / scaling_matrix[param_index, param_index])
                j += 1

        # Exchange rates and times (k >= 0 and t >= 0).
        elif param_name in ['kex', 'ka', 'tex']:
            A.append(zero_array * 0.0)
            A[j][param_index] = 1.0
            b.append(0.0)
            j += 1

    # Convert to numpy data structures.
    A = array(A, float64)
    b = array(b, float64)

    # Return the matrices.
    return A, b


def loop_parameters(spins=None):
    """Generator function for looping of the parameters of the cluster.

    @keyword spins: The list of spin data containers for the block.
    @type spins:    list of SpinContainer instances
    @return:        The parameter name, the parameter index (for the parameter vector), the spin index (for the cluster), and the frequency index (for parameters with different values per spectrometer field strength).
    @rtype:         str, int, int, int
    """

    # The parameter index.
    param_index = -1

    # The R2eff model.
    if cdp.model_type == 'R2eff':
        # Loop over the spins.
        for spin_index in range(len(spins)):
            # Yield the two parameters.
            params = ['r2eff', 'i0']
            for i in range(2):
                # First increment the indices.
                param_index += 1

                # Yield the data.
                yield params[i], param_index, spin_index, None

    # All other models.
    else:
        # First the R2 parameters (one per spin per field strength).
        for spin_index in range(len(spins)):
            # Reset the frequency index.
            frq_index = -1

            # Loop over the spectrometer frequencies.
            for frq in loop_frq():
                # First increment the indices.
                frq_index += 1
                param_index += 1

                # Yield the data.
                yield 'r2', param_index, spin_index, frq_index

        # Then the chemical shift difference parameters 'phi_ex', 'padw2' and 'dw' (one per spin).
        for spin_index in range(len(spins)):
            # Yield the data.
            if 'phi_ex' in spins[spin_index].params:
                param_index += 1
                yield 'phi_ex', param_index, spin_index, None
            if 'padw2' in spins[spin_index].params:
                param_index += 1
                yield 'padw2', param_index, spin_index, None
            if 'dw' in spins[spin_index].params:
                param_index += 1
                yield 'dw', param_index, spin_index, None

        # All other parameters (one per spin cluster).
        for param in spins[0].params:
            if not param in ['r2', 'phi_ex', 'padw2', 'dw']:
                param_index += 1
                yield param, param_index, None, None


def param_index_to_param_info(index=None, spins=None):
    """Convert the given parameter array index to parameter identifying information.
    
    The parameter index will be converted to the parameter name, the relevant spin index in the cluster, and relevant exponential curve key.

    @keyword index: The index of the parameter array.
    @type index:    int
    @keyword spins: The list of spin data containers for the block.
    @type spins:    list of SpinContainer instances
    @return:        The parameter name, the spin index (for the cluster), and the frequency index (for parameters with different values per spectrometer field strength).
    @rtype:         str, int, int
    """

    # Loop over the parameters, yielding when a match is found.
    for param_name, param_index, spin_index, frq_index in loop_parameters(spins=spins):
        if param_index == index:
            return param_name, spin_index, frq_index


def param_num(spins=None):
    """Determine the number of parameters in the model.

    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @return:                The number of model parameters.
    @rtype:                 int
    """

    # The R2eff model.
    if cdp.model_type == 'R2eff':
        # Exponential curves (with clustering).
        if cdp.exp_type in VAR_TIME_EXP:
            return 2 * len(spins)

        # Fixed time period experiments (with clustering).
        else:
            return 1 * len(spins)

    # Check the spin cluster.
    for spin in spins:
        if len(spin.params) != len(spins[0].params):
            raise RelaxError("The number of parameters for each spin in the cluster are not the same.")

    # Count the number of spin specific parameters for all spins.
    spin_params = ['r2', 'phi_ex', 'padw2', 'dw']
    num = 0
    for spin in spins:
        for i in range(len(spin.params)):
            if spin.params[i] in spin_params:
                num += 1

    # Count all other parameters, but only for a single spin.
    for i in range(len(spins[0].params)):
        if not spins[0].params[i] in spin_params:
            num += 1

    # Return the number.
    return num
