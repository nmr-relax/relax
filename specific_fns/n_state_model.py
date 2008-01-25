###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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
from math import pi
from numpy import array, float64, zeros
from re import search

# relax module imports.
from data import Data as relax_data_store
from float import isNaN, isInf
from maths_fns.n_state_model import N_state_opt
from minfx.generic import generic_minimise
from relax_errors import RelaxError, RelaxInfError, RelaxNaNError, RelaxNoModelError
from specific_fns.base_class import Common_functions


class N_state_model(Common_functions):
    """Class containing functions for the N-state model."""

    def assemble_param_vector(self, sim_index=None):
        """Assemble all the parameters of the model into a single array.

        @param sim_index:       The index of the simulation to optimise.  This should be None if
                                normal optimisation is desired.
        @type sim_index:        None or int
        @return:                The parameter vector used for optimisation.
        @rtype:                 numpy array
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Monte Carlo simulation data structures.
        if sim_index != None:
            probs = cdp.probs_sim[sim_index]
            alpha = cdp.alpha_sim[sim_index]
            beta = cdp.beta_sim[sim_index]
            gamma = cdp.gamma_sim[sim_index]

        # Normal data structures.
        else:
            probs = cdp.probs
            alpha = cdp.alpha
            beta = cdp.beta
            gamma = cdp.gamma

        # The probabilities (exclude that of state N).
        param_vector = probs[0:-1]

        # The Euler angles.
        for i in xrange(cdp.N):
            param_vector.append(alpha[i])
            param_vector.append(beta[i])
            param_vector.append(gamma[i])

        # Convert all None values to zero (to avoid conversion to NaN).
        for i in xrange(len(param_vector)):
            if param_vector[i] == None:
                param_vector[i] = 0.0

        # Return a numpy arrary.
        return array(param_vector, float64)


    def default_value(self, param):
        """
        N-state model default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ______________________________________________________________________________________
        |                             |                             |                        |
        | Data type                   | Object name                 | Value                  |
        |_____________________________|_____________________________|________________________|
        |                             |                             |                        |
        | Probabilities               | 'p0', 'p1', 'p2', ..., 'pN' | 1/N                    |
        |                             |                             |                        |
        | Euler angle alpha           | 'alpha0', 'alpha1', ...     | (c+1) * pi / (N+1)     |
        |                             |                             |                        |
        | Euler angle beta            | 'beta0', 'beta1', ...       | (c+1) * pi / (N+1)     |
        |                             |                             |                        |
        | Euler angle gamma           | 'gamma0', 'gamma1', ...     | (c+1) * pi / (N+1)     |
        |_____________________________|_____________________________|________________________|

        In this table, N is the total number of states and c is the index of a given state ranging
        from 0 to N-1.  The default probabilities are all set to be equal whereas the angles are
        given a range of values so that no 2 states are equal at the start of optimisation.

        Note that setting the probability for state N will do nothing as it is equal to one minus
        all the other probabilities.
        """
        __docformat__ = "plaintext"

        # Split the parameter into its base name and index.
        name, index = self.return_data_name(param, index=True)

        # The number of states as a float.
        N = float(relax_data_store[relax_data_store.current_pipe].N)

        # Probability.
        if name == 'probs':
            return 1.0 / N

        # Euler angles.
        elif name == 'alpha' or name == 'beta' or name == 'gamma':
            return (float(index)+1) * pi / (N+1.0)


    def disassemble_param_vector(self, param_vector=None, sim_index=None):
        """Function for disassembling the parameter vector used in the minimisation.

        The parameters are stored in the probability and Euler angle data structures.

        @param param_vector:    The parameter vector returned from optimisation.
        @type param_vector:     numpy array
        @param sim_index:       The index of the simulation to optimise.  This should be None if
                                normal optimisation is desired.
        @type sim_index:        None or int
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Monte Carlo simulation data structures.
        if sim_index != None:
            probs = cdp.probs_sim[sim_index]
            alpha = cdp.alpha_sim[sim_index]
            beta = cdp.beta_sim[sim_index]
            gamma = cdp.gamma_sim[sim_index]

        # Normal data structures.
        else:
            probs = cdp.probs
            alpha = cdp.alpha
            beta = cdp.beta
            gamma = cdp.gamma

        # The probabilities for states 0 to N-1.
        for i in xrange(cdp.N-1):
            probs[i] = param_vector[i]

        # The probability for state N.
        probs[-1] = 1 - sum(probs[0:-1])

        # The Euler angles.
        for i in xrange(cdp.N):
            alpha[i] = param_vector[cdp.N-1 + 3*i]
            beta[i] = param_vector[cdp.N-1 + 3*i + 1]
            gamma[i] = param_vector[cdp.N-1 + 3*i + 2]


    def grid_search(self, lower, upper, inc, constraints=False, verbosity=0, sim_index=None):
        """The grid search function.

        @param lower:       The lower bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          array of int
        @param constraints: If True, constraints are applied during the grid search (elinating parts
                            of the grid).  If False, no constraints are used.
        @type constraints:  bool
        @param verbosity:   A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if the N-state model has been set up.
        if not hasattr(cdp, 'N'):
            raise RelaxNoModelError, 'N-state'

        # The number of parameters.
        n = self.param_num()

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            print "Cannot run a grid search on a model with zero parameters, skipping the grid search."
            return

        # Test the grid search options.
        self.test_grid_ops(lower=lower, upper=upper, inc=inc, n=n)

        # If inc is a single int, convert it into an array of that value.
        if type(inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(inc)
            inc = temp

        # Initialise the grid_ops structure.
        grid_ops = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension has the elements: 0, the number of increments in that
        dimension; 1, the lower limit of the grid; 2, the upper limit of the grid."""

        # Set the grid search options.
        for i in xrange(n):
            # Probabilities (default values).
            if search('^p', cdp.params[i]):
                grid_ops.append([inc[i], 0.0, 1.0])

            # Angles (default values).
            if search('^alpha', cdp.params[i]) or search('^gamma', cdp.params[i]):
                grid_ops.append([inc[i], 0.0, 2*pi])
            elif search('^beta', cdp.params[i]):
                grid_ops.append([inc[i], 0.0, pi])

            # Lower bound (if supplied).
            if lower:
                grid_ops[i][1] = lower[i]

            # Upper bound (if supplied).
            if upper:
                grid_ops[i][1] = upper[i]

        # Minimisation.
        self.minimise(min_algor='grid', min_options=grid_ops, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def is_spin_param(self, name):
        """Determine whether the given parameter is spin specific.

        This method always returns false as there are no spin specific parameters in this type of
        analysis.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        False
        @rtype:         bool
        """

        # Return false.
        return False


    def linear_constraints(self):
        """Function for setting up the linear constraint matrices A and b.

        Standard notation
        =================

        The N-state model constraints are:

            0 <= pc <= 1,

        where p is the probability and c corresponds to state c.


        Matrix notation
        ===============

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are:

            | 1  0  0 |                   |    0    |
            |         |                   |         |
            |-1  0  0 |                   |   -1    |
            |         |     |  p0  |      |         |
            | 0  1  0 |     |      |      |    0    |
            |         |  .  |  p1  |  >=  |         |
            | 0 -1  0 |     |      |      |   -1    |
            |         |     |  p2  |      |         |
            | 0  0  1 |                   |    0    |
            |         |                   |         |
            | 0  0 -1 |                   |   -1    |

        This example is for a 4-state model, the last probability pn is not included as this
        parameter does not exist (because the sum of pc is equal to 1).  The Euler angle parameters
        have been excluded here but will be included in the returned A and b objects.  These
        parameters simply add columns of zero to the A matrix and have no effect on b.


        @return:                The matrices A and b.
        @rtype:                 tuple of len 2 of a numpy matrix and numpy array
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Initialisation (0..j..m).
        A = []
        b = []
        zero_array = zeros(self.param_num(), float64)
        i = 0
        j = 0

        # Loop over the prob parameters (N - 1, because the sum of pc is 1).
        for k in xrange(cdp.N - 1):
            # 0 <= pc <= 1.
            A.append(zero_array * 0.0)
            A.append(zero_array * 0.0)
            A[j][i] = 1.0
            A[j+1][i] = -1.0
            b.append(0.0)
            b.append(-1.0)
            j = j + 2

            # Increment i.
            i = i + 1

        # Convert to numpy data structures.
        A = array(A, float64)
        b = array(b, float64)

        # Return the contraint objects.
        return A, b


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None):
        """Minimisation function.

        @param min_algor:       The minimisation algorithm to use.
        @type min_algor:        str
        @param min_options:     An array of options to be used by the minimisation algorithm.
        @type min_options:      array of str
        @param func_tol:        The function tolerence which, when reached, terminates optimisation.
                                Setting this to None turns of the check.
        @type func_tol:         None or float
        @param grad_tol:        The gradient tolerence which, when reached, terminates optimisation.
                                Setting this to None turns of the check.
        @type grad_tol:         None or float
        @param max_iterations:  The maximum number of iterations for the algorithm.
        @type max_iterations:   int
        @param constraints:     If True, constraints are used during optimisation.
        @type constraints:      bool
        @param scaling:         If True, diagonal scaling is enabled during optimisation to allow
                                the problem to be better conditioned.
        @type scaling:          bool
        @param verbosity:       A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @param sim_index:       The index of the simulation to optimise.  This should be None if
                                normal optimisation is desired.
        @type sim_index:        None or int
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if the N-state model has been set up.
        if not hasattr(cdp, 'N'):
            raise RelaxNoModelError, 'N-state'

        # Create the initial parameter vector.
        param_vector = self.assemble_param_vector(sim_index=sim_index)

        # Linear constraints.
        if constraints:
            A, b = self.linear_constraints()

        # Create a list of matricies consisting of all the full alignment tensors.
        full_tensors = []
        for tensor in cdp.align_tensors:
            # Ignore the reduced tensors.
            if tensor.red:
                continue

            # Append the tensor (in matrix form).
            full_tensors.append(tensor.tensor)

        # Create a list of all the reduced alignment tensor elements and their errors (for the chi-squared function).
        red_tensor_elem = []
        red_tensor_err = []
        for tensor in cdp.align_tensors:
            # Ignore the full tensors.
            if not tensor.red:
                continue

            # Append the 5 unique elements.
            red_tensor_elem.append(tensor.Sxx)
            red_tensor_elem.append(tensor.Syy)
            red_tensor_elem.append(tensor.Sxy)
            red_tensor_elem.append(tensor.Sxz)
            red_tensor_elem.append(tensor.Syz)

            # Append the 5 unique error elements (if they exist).
            if hasattr(tensor, 'Sxx_err'):
                red_tensor_err.append(tensor.Sxx_err)
                red_tensor_err.append(tensor.Syy_err)
                red_tensor_err.append(tensor.Sxy_err)
                red_tensor_err.append(tensor.Sxz_err)
                red_tensor_err.append(tensor.Syz_err)

            # Otherwise append errors of 1.0 to convert the chi-squared equation to the SSE equation (for the tensors without errors).
            else:
                red_tensor_err = red_tensor_err + [1.0, 1.0, 1.0, 1.0, 1.0]

        # Convert the reduced alignment tensor element lists into numpy arrays (for the chi-squared function maths).
        red_tensor_elem = array(red_tensor_elem, float64)
        red_tensor_err = array(red_tensor_err, float64)

        # Set up the class instance containing the target function.
        model = N_state_opt(N=cdp.N, init_params=param_vector, full_tensors=full_tensors, red_data=red_tensor_elem, red_errors=red_tensor_err)

        # Minimisation.
        if constraints:
            results = generic_minimise(func=model.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)
        else:
            results = generic_minimise(func=model.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=verbosity)
        if results == None:
            return
        param_vector, func, iter_count, f_count, g_count, h_count, warning = results

        # Catch infinite chi-squared values.
        if isInf(func):
            raise RelaxInfError, 'chi-squared'

        # Catch chi-squared values of NaN.
        if isNaN(func):
            raise RelaxNaNError, 'chi-squared'

        # Disassemble the parameter vector.
        self.disassemble_param_vector(param_vector=param_vector, sim_index=sim_index)

        # Monte Carlo minimisation statistics.
        if sim_index != None:
            # Chi-squared statistic.
            cdp.chi2_sim[sim_index] = func

            # Iterations.
            cdp.iter_sim[sim_index] = iter_count

            # Function evaluations.
            cdp.f_count_sim[sim_index] = f_count

            # Gradient evaluations.
            cdp.g_count_sim[sim_index] = g_count

            # Hessian evaluations.
            cdp.h_count_sim[sim_index] = h_count

            # Warning.
            cdp.warning_sim[sim_index] = warning

        # Normal statistics.
        else:
            # Chi-squared statistic.
            cdp.chi2 = func

            # Iterations.
            cdp.iter = iter_count

            # Function evaluations.
            cdp.f_count = f_count

            # Gradient evaluations.
            cdp.g_count = g_count

            # Hessian evaluations.
            cdp.h_count = h_count

            # Warning.
            cdp.warning = warning


    def model_setup(self, N=None):
        """Function for setting up the N-state model.

        @param N:   The number of states.
        @type N:    int
        """

        # Test if the current data pipe exists.
        if not relax_data_store.current_pipe:
            raise RelaxNoPipeError

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Set the value of N.
        cdp.N = N

        # Initialise the list of model parameters.
        cdp.params = []

        # Add the probability parameters.
        for i in xrange(N-1):
            cdp.params.append('p' + `i`)

        # Add the Euler angle parameters.
        for i in xrange(N):
            cdp.params.append('alpha' + `i`)
            cdp.params.append('beta' + `i`)
            cdp.params.append('gamma' + `i`)

        # Initialise the probability and Euler angle arrays.
        cdp.probs = [None] * cdp.N
        cdp.alpha = [None] * cdp.N
        cdp.beta = [None] * cdp.N
        cdp.gamma = [None] * cdp.N


    def param_num(self):
        """Function for determining the number of parameters in the model.

        @return:    The number of model parameters.
        @rtype:     int
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Return the param number.
        return (cdp.N - 1) + cdp.N*3


    def return_data_name(self, name, index=False):
        """
        N-state model data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |                             |                                   |
        | Data type              | Object name                 | Patterns                          |
        |________________________|_____________________________|___________________________________|
        |                        |                             |                                   |
        | Probabilities          | 'probs'                     | 'p0', 'p1', 'p2', ..., 'pN'       |
        |                        |                             |                                   |
        | Euler angle alpha      | 'alpha'                     | 'alpha0', 'alpha1', ...           |
        |                        |                             |                                   |
        | Euler angle beta       | 'beta'                      | 'beta0', 'beta1', ...             |
        |                        |                             |                                   |
        | Euler angle gamma      | 'gamma'                     | 'gamma0', 'gamma1', ...           |
        |________________________|_____________________________|___________________________________|

        The objects corresponding to the object names are lists (or arrays) with each element
        corrsponding to each state.
        """
        __docformat__ = "plaintext"

        # Probability.
        if search('^p', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[1:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'probs', i
            else:
                return 'probs'

        # Alpha Euler angle.
        if search('^alpha', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[5:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'alpha', i
            else:
                return 'alpha'

        # Beta Euler angle.
        if search('^beta', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[4:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'beta', i
            else:
                return 'beta'

        # Gamma Euler angle.
        if search('^gamma', name):
            # Get the state index, otherwise return with nothing if there is an error (parameter unknown).
            try:
                i = int(name[5:])
            except ValueError:
                return

            # Return the name (and maybe index).
            if index:
                return 'gamma', i
            else:
                return 'gamma'


    def set_doc(self):
        """
        N-state model set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~

        Setting parameters for the N-state model is a little different from the other type of
        analyses as each state has a set of parameters with the same names as the other states.
        To set the parameters for a specific state c (ranging from 0 for the first to N-1 for the
        last, the number c should be added to the end of the parameter name.  So the Euler angle
        gamma of the third state is specified using the string 'gamma2'.
        """
        __docformat__ = "plaintext"


    def set_domain(self, tensor=None, domain=None):
        """Set the domain label for the given tensor.

        @param tensor:  The alignment tensor label.
        @type tensor:   str
        @param domain:  The domain label.
        @type domain:   str
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Loop over the tensors.
        match = False
        for tensor_cont in cdp.align_tensors:
            # Find the matching tensor and then store the domain label.
            if tensor_cont.name == tensor:
                tensor_cont.domain = domain
                match = True

        # The tensor label doesn't exist.
        if not match:
            raise RelaxNoTensorError, ('alignment', tensor)


    def set_non_spin_params(self, value=None, param=None):
        """Function for setting all the N-state model parameter values.

        @param value:   The parameter values (for defaults supply [None]).
        @type value:    list of numbers or [None]
        @param param:   The parameter names.
        @type param:    None, str, or list of str
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test if the N-state model has been set up.
        if not hasattr(cdp, 'N'):
            raise RelaxNoModelError, 'N-state'

        # Get the model parameters if param is None.
        if param == None:
            param = cdp.params

        # Test that the parameter and value lists are the same size.
        if type(param) == list and value[0] != None and len(param) != len(value):
            raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to the length of the parameter array, " + `param` + "."

        # Convert param to a list (if it is a string).
        if type(param) == str:
            param = [param]

        # If no value is supplied (i.e. value == [None]), then get the default values.
        if value == [None]:
            value = []
            for i in xrange(len(param)):
                value.append(self.default_value(param[i]))

        # Set the parameter values.
        for i in xrange(len(param)):
            # Get the object name and the parameter index.
            object_name, index = self.return_data_name(param[i], index=True)
            if not object_name:
                raise RelaxError, "The data type " + `param[i]` + " does not exist."

            # Get the object.
            object = getattr(cdp, object_name)

            # Set the parameter value.
            object[index] = value[i]


    def set_type(self, tensor=None, red=None):
        """Set the whether the given tensor is the full or reduced tensor.

        @param tensor:  The alignment tensor label.
        @type tensor:   str
        @param red:     The flag specifying whether the given tensor is the full or reduced tensor.
        @type red:      bool
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Loop over the tensors.
        match = False
        for tensor_cont in cdp.align_tensors:
            # Find the matching tensor and then store the tensor type.
            if tensor_cont.name == tensor:
                tensor_cont.red = red
                match = True

        # The tensor label doesn't exist.
        if not match:
            raise RelaxNoTensorError, ('alignment', tensor)
