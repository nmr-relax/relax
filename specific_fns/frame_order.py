###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module for the specific methods of the Frame Order theories."""

# Python module imports.
from math import pi
from minfx.generic import generic_minimise
from numpy import array, float64, ones, zeros

# relax module imports.
from float import isNaN, isInf
from generic_fns import pipes
from maths_fns import frame_order_models
from relax_errors import RelaxInfError, RelaxNaNError, RelaxNoModelError
from specific_fns.base_class import Common_functions


class Frame_order(Common_functions):
    """Class containing the specific methods of the Frame Order theories."""

    def __minimise_setup_tensors(self):
        """Set up the data structures for optimisation using alignment tensors as base data sets.

        @return:    The assembled data structures for using alignment tensors as the base data for
                    optimisation.  These include:
                        - full_tensors, the full tensors as concatenated 5D, rank-1 arrays.
                        - red_tensors, the reduced tensors as concatenated 5D, rank-1 arrays.
                        - red_err, the reduced tensor errors as concatenated 5D, rank-1 arrays.
        @rtype:     tuple of 3 numpy nx5D, rank-1 arrays
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Number of tensor pairs.
        n = len(cdp.align_tensors.reduction)

        # Initialise.
        full_tensors = zeros(n*5, float64)
        red_tensors  = zeros(n*5, float64)
        red_err = ones(n*5, float64) * 1e-7
        data = cdp.align_tensors
        list = data.reduction

        # Loop over the reduction list.
        for i in range(n):
            # The full tensor.
            full_tensors[5*i + 0] = data[list[i][0]].Axx
            full_tensors[5*i + 1] = data[list[i][0]].Ayy
            full_tensors[5*i + 2] = data[list[i][0]].Axy
            full_tensors[5*i + 3] = data[list[i][0]].Axz
            full_tensors[5*i + 4] = data[list[i][0]].Ayz

            # The reduced tensor.
            red_tensors[5*i + 0] = data[list[i][1]].Axx
            red_tensors[5*i + 1] = data[list[i][1]].Ayy
            red_tensors[5*i + 2] = data[list[i][1]].Axy
            red_tensors[5*i + 3] = data[list[i][1]].Axz
            red_tensors[5*i + 4] = data[list[i][1]].Ayz

            # The reduced tensor errors.
            if hasattr(data[list[i][1]], 'Axx_err'):
                red_err[5*i + 0] = data[list[i][1]].Axx_err
                red_err[5*i + 1] = data[list[i][1]].Ayy_err
                red_err[5*i + 2] = data[list[i][1]].Axy_err
                red_err[5*i + 3] = data[list[i][1]].Axz_err
                red_err[5*i + 4] = data[list[i][1]].Ayz_err

        # Return the data structures.
        return full_tensors, red_tensors, red_err


    def __update_model(self):
        """Update the model parameters as necessary."""

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Initialise the list of model parameters.
        if not hasattr(cdp, 'params'):
            cdp.params = []

        # Isotropic cone model.
        if cdp.model == 'iso cone':
            # Set up the parameter arrays.
            if not len(cdp.params):
                cdp.params.append('theta_axis')
                cdp.params.append('phi_axis')
                cdp.params.append('theta_cone')

            # Initialise the cone axis angles and cone angle values.
            if not hasattr(cdp, 'theta_axis'):
                cdp.theta_axis = 0.0
            if not hasattr(cdp, 'phi_axis'):
                cdp.phi_axis = 0.0
            if not hasattr(cdp, 'theta_cone'):
                cdp.theta_cone = 0.0


    def __unpack_opt_results(self, results, sim_index=None):
        """Unpack and store the Frame Order optimisation results.

        @param results:     The results tuple returned by the minfx generic_minimise() function.
        @type results:      tuple
        @param sim_index:   The index of the simulation to optimise.  This should be None for normal
                            optimisation.
        @type sim_index:    None or int
         """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Disassemble the results.
        param_vector, func, iter_count, f_count, g_count, h_count, warning = results

        # Catch infinite chi-squared values.
        if isInf(func):
            raise RelaxInfError, 'chi-squared'

        # Catch chi-squared values of NaN.
        if isNaN(func):
            raise RelaxNaNError, 'chi-squared'

        # Isotropic cone model.
        if cdp.model == 'iso cone':
            # Disassemble the parameter vector.
            theta_axis, phi_axis, theta_cone = param_vector

            # Wrap the cone angle to be between 0 and pi.
            if theta_cone < 0.0:
                theta_cone = -theta_cone
            if theta_cone > pi:
                theta_cone = 2.0*pi - theta_cone

            # Monte Carlo simulation data structures.
            if sim_index != None:
                # Model parameters.
                cdp.theta_axis_sim[sim_index] = theta_axis
                cdp.phi_axis_sim[sim_index] = phi_axis
                cdp.theta_cone_sim[sim_index] = theta_cone

                # Optimisation info.
                cdp.chi2_sim[sim_index] = func
                cdp.iter_sim[sim_index] = iter_count
                cdp.f_count_sim[sim_index] = f_count
                cdp.g_count_sim[sim_index] = g_count
                cdp.h_count_sim[sim_index] = h_count
                cdp.warning_sim[sim_index] = warning

            # Normal data structures.
            else:
                # Model parameters.
                cdp.theta_axis = theta_axis
                cdp.phi_axis = phi_axis
                cdp.theta_cone = theta_cone

                # Optimisation info.
                cdp.chi2 = func
                cdp.iter = iter_count
                cdp.f_count = f_count
                cdp.g_count = g_count
                cdp.h_count = h_count
                cdp.warning = warning


    def grid_search(self, lower, upper, inc, constraints=False, verbosity=0, sim_index=None):
        """Perform a grid search.

        @param lower:       The lower bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          int or array of int
        @param constraints: If True, constraints are applied during the grid search (eliminating
                            parts of the grid).  If False, no constraints are used.
        @type constraints:  bool
        @param verbosity:   A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        """

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the Frame Order model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError, 'Frame Order'

        # The number of parameters.
        n = len(cdp.params)

        # If inc is an int, convert it into an array of that value.
        if type(inc) == int:
            inc = [inc]*n

        # Initialise the grid_ops structure.
        grid_ops = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension has the elements: 0, the number of increments in that
        dimension; 1, the lower limit of the grid; 2, the upper limit of the grid."""

        # Set the grid search options.
        for i in xrange(n):
            # Cone axis angles and cone angle.
            if cdp.params[i] == 'phi_axis':
                grid_ops.append([inc[i], 0.0, pi])
            if cdp.params[i] == 'theta_axis':
                grid_ops.append([inc[i], 0.0, pi])
            if cdp.params[i] == 'theta_cone':
                grid_ops.append([inc[i], 0.0, pi])

            # Lower bound (if supplied).
            if lower:
                grid_ops[i][1] = lower[i]

            # Upper bound (if supplied).
            if upper:
                grid_ops[i][1] = upper[i]

        # Minimisation.
        self.minimise(min_algor='grid', min_options=grid_ops, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None):
        """Minimisation function.

        @param min_algor:       The minimisation algorithm to use.
        @type min_algor:        str
        @param min_options:     An array of options to be used by the minimisation algorithm.
        @type min_options:      array of str
        @param func_tol:        The function tolerance which, when reached, terminates optimisation.
                                Setting this to None turns of the check.
        @type func_tol:         None or float
        @param grad_tol:        The gradient tolerance which, when reached, terminates optimisation.
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
        cdp = pipes.get_pipe()

        # Isotropic cone model.
        if cdp.model == 'iso cone':
            # The initial parameter vector (the cone axis angles and the cone angle).
            param_vector = array([cdp.theta_axis, cdp.phi_axis, cdp.theta_cone], float64)

            # Get the data structures for optimisation using the tensors as base data sets.
            full_tensors, red_tensors, red_tensor_err = self.__minimise_setup_tensors()

            # Set up the optimisation function.
            target = frame_order_models.Frame_order(model=cdp.model, full_tensors=full_tensors, red_tensors=red_tensors, red_errors=red_tensor_err)

        # Minimisation.
        results = generic_minimise(func=target.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=verbosity)

        # Unpack the results.
        self.__unpack_opt_results(results, sim_index)


    def select_model(self, model=None):
        """Select the Frame Order model.

        @param model:   The Frame Order model.  As of yet, this can only be 'iso cone'.
        @type model:    str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Test if the model is already setup.
        if hasattr(cdp, 'model'):
            raise RelaxModelError, 'Frame Order'

        # Test if the model name exists.
        if not model in ['iso cone']:
            raise RelaxError, "The model name " + `model` + " is invalid."

        # Set the model
        cdp.model = model

        # Initialise the list of model parameters.
        cdp.params = []

        # Update the model.
        self.__update_model()
