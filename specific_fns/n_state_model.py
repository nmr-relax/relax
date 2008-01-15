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
from numpy import array, float64, zeros
from re import search

# relax module imports.
from data import Data as relax_data_store
from maths_fns.n_state_model import N_state_opt
from minimise.generic import generic_minimise
from relax_errors import RelaxNoModelError
from specific_fns.base_class import Common_functions


class N_state_model(Common_functions):
    """Class containing functions for the N-state model."""

    def assemble_param_vector(self, sim_index):
        """Assemble all the parameters of the model into a single array."""

        # Initialise.
        param_vector = []

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # The probabilities.
        #for i in xrange(len(cdp.align

        # Return a numpy arrary.
        return array(param_vector, float64)


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

        # Test the grid search options.
        self.test_grid_ops(lower=lower, upper=upper, inc=inc, n=n)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            print "Cannot run a grid search on a model with zero parameters, skipping the grid search."
            return

        # Initialise the grid_ops structure.
        grid_ops = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension has the elements: 0, the number of increments in that
        dimension; 1, the lower limit of the grid; 2, the upper limit of the grid."""

        # Set the grid search options.
        for i in xrange(n):
            # Probabilities (default values).
            if cdp.params[i] == 'pc':
                grid_ops.append([inc[m], 0.0, 1.0])

            # Angles (default values).
            if cdp.params[i] == 'alpha' or cdp.params[i] == 'gamma':
                grid_ops.append([inc[m], 0.0, 2*pi])
            elif cdp.params[i] == 'beta':
                grid_ops.append([inc[m], 0.0, pi])

            # Lower bound (if supplied).
            if lower:
                grid_ops[i][1] = lower[i]

            # Upper bound (if supplied).
            if upper:
                grid_ops[i][1] = upper[i]

        print `grid_ops`

        # Minimisation.
        self.minimise(min_algor='grid', min_options=grid_ops, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


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
        model = N_state_opt(init_params=param_vector, red_data=red_tensor_elem, red_errors=red_tensor_err)

        # Minimisation.
        if constraints:
            results = generic_minimise(func=model.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=verbosity)
        else:
            results = generic_minimise(func=model.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=verbosity)
        if results == None:
            return
        param_vector, func, iter_count, f_count, g_count, h_count, warning = results


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


    def param_num(self):
        """Function for determining the number of parameters in the model.

        @return:    The number of model parameters.
        @rtype:     int
        """

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Return the param number.
        return (cdp.N - 1) + cdp.N*3


    def return_data_name(self, name):
        """
        N-state model data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Bond length            | 'r'          | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |                        |              |                                                  |
        | CSA                    | 'csa'        | '^[Cc][Ss][Aa]$'                                 |
        |________________________|______________|__________________________________________________|

        """
        __docformat__ = "plaintext"

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'


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
