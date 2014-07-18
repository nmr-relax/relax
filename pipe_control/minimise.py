###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
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
"""Module for model minimisation/optimisation."""

# Python module imports.
from numpy import float64, identity

# relax module imports.
from lib.errors import RelaxError, RelaxIntListIntError, RelaxLenError
from multi import Processor_box
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control import pipes
from specific_analyses.api import return_api, return_parameter_object
from status import Status; status = Status()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()


def assemble_scaling_matrix(scaling=True):
    """Create and return the per-model scaling matrices.

    @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
    @type scaling:              bool
    @return:                    The list of diagonal and square scaling matrices.
    @rtype:                     list of numpy rank-2, float64 array or list of None
    """

    # The specific analysis API object and parameter object.
    api = return_api()
    param_object = return_parameter_object()

    # Initialise.
    scaling_matrix = []

    # Loop over the models.
    for model_info in api.model_loop():
        # No diagonal scaling.
        if not scaling:
            scaling_matrix.append(None)
            continue

        # Get the parameter names.
        names = api.get_param_names(model_info)

        # The parameter number.
        n = len(names)

        # Initialise.
        scaling_matrix.append(identity(n, float64))
        i = 0

        # Update the diagonal with the parameter specific scaling factor.
        for i in range(n):
            scaling_matrix[-1][i, i] = param_object.scaling(names[i], model_info=model_info)

    # Return the matrix.
    return scaling_matrix


def calc(verbosity=1):
    """Function for calculating the function value.

    @param verbosity:   The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:    int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The specific analysis API object.
    api = return_api()

    # Deselect spins lacking data:
    api.overfit_deselect()

    # Create the scaling matrix.
    scaling_matrix = assemble_scaling_matrix()

    # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
    processor_box = Processor_box() 
    processor = processor_box.processor

    # Monte Carlo simulation calculation.
    if hasattr(cdp, 'sim_state') and cdp.sim_state == 1:
        # Loop over the simulations.
        for i in range(cdp.sim_number):
            # Status.
            if status.current_analysis:
                status.auto_analysis[status.current_analysis].mc_number = i
            else:
                status.mc_number = i

            # Calculation.
            api.calculate(verbosity=verbosity-1, sim_index=i, scaling_matrix=scaling_matrix)

            # Print out.
            if verbosity and not processor.is_queued():
                print("Simulation " + repr(i+1))

        # Unset the status.
        if status.current_analysis:
            status.auto_analysis[status.current_analysis].mc_number = None
        else:
            status.mc_number = None

    # Minimisation.
    else:
        api.calculate(verbosity=verbosity, scaling_matrix=scaling_matrix)

    # Execute any queued commands.
    processor.run_queue()


def grid_search(lower=None, upper=None, inc=None, constraints=True, verbosity=1):
    """The grid search function.

    @param lower:       The lower bounds of the grid search which must be equal to the number of parameters in the model.
    @type lower:        array of numbers
    @param upper:       The upper bounds of the grid search which must be equal to the number of parameters in the model.
    @type upper:        array of numbers
    @param inc:         The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.
    @type inc:          int or list of int
    @param constraints: If True, constraints are applied during the grid search (elinating parts of the grid).  If False, no constraints are used.
    @type constraints:  bool
    @param verbosity:   The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:    int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The specific analysis API object.
    api = return_api()

    # Deselect models lacking data:
    api.overfit_deselect()

    # Determine the model specific grid bounds, and allow for the zooming grid search, and check the inc argument.
    model_lower, model_upper, model_inc = grid_setup(lower, upper, inc)

    # Create the scaling matrix.
    scaling_matrix = assemble_scaling_matrix()

    # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
    processor_box = Processor_box() 
    processor = processor_box.processor

    # Monte Carlo simulation grid search.
    if hasattr(cdp, 'sim_state') and cdp.sim_state == 1:
        # Loop over the simulations.
        for i in range(cdp.sim_number):
            # Status.
            if status.current_analysis:
                status.auto_analysis[status.current_analysis].mc_number = i
            else:
                status.mc_number = i

            # Optimisation.
            api.grid_search(lower=model_lower, upper=model_upper, inc=model_inc, scaling_matrix=scaling_matrix, constraints=constraints, verbosity=verbosity-1, sim_index=i)

            # Print out.
            if verbosity and not processor.is_queued():
                print("Simulation " + repr(i+1))

        # Unset the status.
        if status.current_analysis:
            status.auto_analysis[status.current_analysis].mc_number = None
        else:
            status.mc_number = None

    # Grid search.
    else:
        api.grid_search(lower=model_lower, upper=model_upper, inc=model_inc, scaling_matrix=scaling_matrix, constraints=constraints, verbosity=verbosity)

    # Execute any queued commands.
    processor.run_queue()


def grid_setup(lower=None, upper=None, inc=None):
    """Determine the per-model grid bounds, allowing for the zooming grid search.

    @keyword lower:     The user supplied lower bounds of the grid search which must be equal to the number of parameters in the model.
    @type lower:        list of numbers
    @keyword upper:     The user supplied upper bounds of the grid search which must be equal to the number of parameters in the model.
    @type upper:        list of numbers
    @keyword inc:       The user supplied grid search increments.
    @type inc:          int or list of int
    @return:            The per-model grid upper and lower bounds.  The first dimension of each structure corresponds to the model, the second the model parameters.
    @rtype:             tuple of lists of lists of float, lists of lists of float, list of lists of int
    """

    # The specific analysis API object and parameter object.
    api = return_api()
    param_object = return_parameter_object()

    # Initialise.
    model_lower = []
    model_upper = []
    model_inc = []

    # Loop over the models.
    for model_info in api.model_loop():
        # Get the parameter names and current values.
        names = api.get_param_names(model_info)
        values = api.get_param_values(model_info)

        # The parameter number.
        n = len(names)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError("Cannot run a grid search on a model with zero parameters.")

        # Check the user supplied increments.
        if isinstance(inc, list) and len(inc) != n:
            raise RelaxLenError('increment', n)
        if isinstance(inc, list):
            for i in range(n):
                if not (isinstance(inc[i], int) or inc[i] == None):
                    raise RelaxIntListIntError('increment', inc)
        elif not isinstance(inc, int):
            raise RelaxIntListIntError('increment', inc)

        # Convert to the model increment list.
        if isinstance(inc, int):
            model_inc.append([inc]*n)
        else:
            model_inc.append(inc)

        # The lower and upper bounds have been supplied by the user, so use those unmodified instead.
        if lower != None or upper != None:
            # Check that the user supplied bound lengths are ok.
            if len(lower) != n:
                raise RelaxLenError('lower bounds', n)
            if len(upper) != n:
                raise RelaxLenError('upper bounds', n)

            # Append the values.
            model_lower.append(lower)
            model_upper.append(upper)

            # Skip the rest of the loop.
            continue

        # Print out the model title.
        api.print_model_title(model_info)

        # Build the bounds.
        model_lower.append([])
        model_upper.append([])
        for i in range(n):
            # Obtain the bounds.
            lower_i = param_object.grid_lower(names[i], model_info=model_info)
            upper_i = param_object.grid_upper(names[i], model_info=model_info)

            # Scale the bounds.
            lower_i /= param_object.scaling(names[i], model_info=model_info)
            upper_i /= param_object.scaling(names[i], model_info=model_info)

            # Append.
            model_lower[-1].append(lower_i)
            model_upper[-1].append(upper_i)

    # Return the bounds.
    return model_lower, model_upper, model_inc


def grid_zoom(level=0):
    """Store the grid zoom level.

    The zoom level can be one of:

        0:  No zooming - setting this value will deactivate the zooming grid search.
        1:  1st level zoom.  This will activate the first zoom level.  For the frame order parameters, excluding the pivot point, this will halve the grid upper and lower bound values and center the grid at the current parameter values.
        2:  2nd level zoom.  This will activate the second zoom level.  For the frame order parameters, excluding the pivot point, this will zoom the grid upper and lower bound values by a quarter (1/2^2).
        3:  3rd level zoom.  This will activate the second zoom level.  For the frame order parameters, excluding the pivot point, this will zoom the grid upper and lower bound values by an eighth (1/2^3).


    @keyword level: The zoom level.
    @type level:    int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Check the value.
    allowed = [0, 1, 2, 3]
    if level not in allowed:
        raise RelaxError("The grid zoom level of '%s' is not valid, it must be one of %s." % (level, allowed))

    # Store the values.
    cdp.grid_zoom_level = level


def minimise(min_algor=None, line_search=None, hessian_mod=None, hessian_type=None, func_tol=None, grad_tol=None, max_iter=None, constraints=True, scaling=True, verbosity=1, sim_index=None):
    """Minimisation function.

    @keyword min_algor:         The minimisation algorithm to use.
    @type min_algor:            str
    @keyword line_search:       The line search algorithm which will only be used in combination with the line search and conjugate gradient methods.  This will default to the More and Thuente line search.
    @type line_search:          str or None
    @keyword hessian_mod:       The Hessian modification.  This will only be used in the algorithms which use the Hessian, and defaults to Gill, Murray, and Wright modified Cholesky algorithm.
    @type hessian_mod:          str or None
    @keyword hessian_type:      The Hessian type.  This will only be used in a few trust region algorithms, and defaults to BFGS.
    @type hessian_type:         str or None
    @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
    @type func_tol:             None or float
    @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
    @type grad_tol:             None or float
    @keyword max_iter:          The maximum number of iterations for the algorithm.
    @type max_iter:             int
    @keyword constraints:       If True, constraints are used during optimisation.
    @type constraints:          bool
    @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
    @type scaling:              bool
    @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:            int
    @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:            None or int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The specific analysis API object.
    api = return_api()

    # Re-package the minimisation algorithm, options, and constraints for the generic_minimise() calls within the specific code.
    if constraints:
        min_options = [min_algor]

        # Determine the constraint algorithm to use.
        min_algor = api.constraint_algorithm()
    else:
        min_options = []
    if line_search != None:
        min_options.append(line_search)
    if hessian_mod != None:
        min_options.append(hessian_mod)
    if hessian_type != None:
        min_options.append(hessian_type)
    min_options = tuple(min_options)

    # Deselect spins lacking data:
    api.overfit_deselect()

    # Create the scaling matrix.
    scaling_matrix = assemble_scaling_matrix(scaling)

    # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
    processor_box = Processor_box() 
    processor = processor_box.processor

    # Single Monte Carlo simulation.
    if sim_index != None:
        api.minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iter, constraints=constraints, scaling_matrix=scaling_matrix, verbosity=verbosity, sim_index=sim_index)

    # Monte Carlo simulation minimisation.
    elif hasattr(cdp, 'sim_state') and cdp.sim_state == 1:
        for i in range(cdp.sim_number):
            # Status.
            if status.current_analysis:
                status.auto_analysis[status.current_analysis].mc_number = i
            else:
                status.mc_number = i

            # Optimisation.
            api.minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iter, constraints=constraints, scaling_matrix=scaling_matrix, verbosity=verbosity-1, sim_index=i)

            # Print out.
            if verbosity and not processor.is_queued():
                print("Simulation " + repr(i+1))

        # Unset the status.
        if status.current_analysis:
            status.auto_analysis[status.current_analysis].mc_number = None
        else:
            status.mc_number = None

    # Standard minimisation.
    else:
        api.minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iter, constraints=constraints, scaling_matrix=scaling_matrix, verbosity=verbosity)

    # Execute any queued commands.
    processor.run_queue()


def reset_min_stats(data_pipe=None, spin=None):
    """Function for resetting the minimisation statistics.

    @param data_pipe:   The name of the data pipe to reset the minimisation statisics of.  This defaults to the current data pipe.
    @type data_pipe:    str
    @param spin:        The spin data container if spin specific data is to be reset.
    @type spin:         SpinContainer
    """

    # The data pipe.
    if data_pipe == None:
        data_pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(data_pipe)


    # Global minimisation statistics.
    #################################

    # Chi-squared.
    if hasattr(dp, 'chi2'):
        dp.chi2 = None

    # Iteration count.
    if hasattr(dp, 'iter'):
        dp.iter = None

    # Function count.
    if hasattr(dp, 'f_count'):
        dp.f_count = None

    # Gradient count.
    if hasattr(dp, 'g_count'):
        dp.g_count = None

    # Hessian count.
    if hasattr(dp, 'h_count'):
        dp.h_count = None

    # Warning.
    if hasattr(dp, 'warning'):
        dp.warning = None


    # Sequence specific minimisation statistics.
    ############################################

    # Loop over all spins.
    for spin in spin_loop():
        # Chi-squared.
        if hasattr(spin, 'chi2'):
            spin.chi2 = None

        # Iteration count.
        if hasattr(spin, 'iter'):
            spin.iter = None

        # Function count.
        if hasattr(spin, 'f_count'):
            spin.f_count = None

        # Gradient count.
        if hasattr(spin, 'g_count'):
            spin.g_count = None

        # Hessian count.
        if hasattr(spin, 'h_count'):
            spin.h_count = None

        # Warning.
        if hasattr(spin, 'warning'):
            spin.warning = None


def set(val=None, error=None, param=None, scaling=None, spin_id=None):
    """Set global or spin specific minimisation parameters.

    @keyword val:       The parameter values.
    @type val:          number
    @keyword param:     The parameter names.
    @type param:        str
    @keyword scaling:   Unused.
    @type scaling:      float
    @keyword spin_id:   The spin identification string.
    @type spin_id:      str
    """

    # Global minimisation stats.
    if spin_id == None:
        # Chi-squared.
        if param == 'chi2':
            cdp.chi2 = val

        # Iteration count.
        elif param == 'iter':
            cdp.iter = val

        # Function call count.
        elif param == 'f_count':
            cdp.f_count = val

        # Gradient call count.
        elif param == 'g_count':
            cdp.g_count = val

        # Hessian call count.
        elif param == 'h_count':
            cdp.h_count = val

    # Residue specific minimisation.
    else:
        # Get the spin.
        spin = return_spin(spin_id)

        # Chi-squared.
        if param == 'chi2':
            spin.chi2 = val

        # Iteration count.
        elif param == 'iter':
            spin.iter = val

        # Function call count.
        elif param == 'f_count':
            spin.f_count = val

        # Gradient call count.
        elif param == 'g_count':
            spin.g_count = val

        # Hessian call count.
        elif param == 'h_count':
            spin.h_count = val
