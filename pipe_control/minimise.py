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

# relax module imports.
from multi import Processor_box
from pipe_control.mol_res_spin import return_spin, spin_loop
from pipe_control import pipes
from specific_analyses.api import return_api
from status import Status; status = Status()
from user_functions.data import Uf_tables; uf_tables = Uf_tables()


def calc(verbosity=1):
    """Function for calculating the function value.

    @param verbosity:   The amount of information to print.  The higher the value, the greater
                        the verbosity.
    @type verbosity:    int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The specific analysis API object.
    api = return_api()

    # Deselect spins lacking data:
    api.overfit_deselect()

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
            api.calculate(verbosity=verbosity-1, sim_index=i)

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
        api.calculate(verbosity=verbosity)

    # Execute any queued commands.
    processor.run_queue()


def grid_search(lower=None, upper=None, inc=None, constraints=True, verbosity=1):
    """The grid search function.

    @param lower:       The lower bounds of the grid search which must be equal to the number of
                        parameters in the model.
    @type lower:        array of numbers
    @param upper:       The upper bounds of the grid search which must be equal to the number of
                        parameters in the model.
    @type upper:        array of numbers
    @param inc:         The increments for each dimension of the space for the grid search.  The
                        number of elements in the array must equal to the number of parameters in
                        the model.
    @type inc:          array of int
    @param constraints: If True, constraints are applied during the grid search (elinating parts of
                        the grid).  If False, no constraints are used.
    @type constraints:  bool
    @param verbosity:   The amount of information to print.  The higher the value, the greater
                        the verbosity.
    @type verbosity:    int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The specific analysis API object.
    api = return_api()

    # Deselect spins lacking data:
    api.overfit_deselect()

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
            api.grid_search(lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity-1, sim_index=i)

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
        api.grid_search(lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity)

    # Execute any queued commands.
    processor.run_queue()


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

    # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
    processor_box = Processor_box() 
    processor = processor_box.processor

    # Single Monte Carlo simulation.
    if sim_index != None:
        api.minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iter, constraints=constraints, scaling=scaling, verbosity=verbosity, sim_index=sim_index)

    # Monte Carlo simulation minimisation.
    elif hasattr(cdp, 'sim_state') and cdp.sim_state == 1:
        for i in range(cdp.sim_number):
            # Status.
            if status.current_analysis:
                status.auto_analysis[status.current_analysis].mc_number = i
            else:
                status.mc_number = i

            # Optimisation.
            api.minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iter, constraints=constraints, scaling=scaling, verbosity=verbosity-1, sim_index=i)

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
        api.minimise(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iter, constraints=constraints, scaling=scaling, verbosity=verbosity)

    # Execute any queued commands.
    processor.run_queue()


def reset_min_stats(data_pipe=None, spin=None):
    """Function for resetting the minimisation statistics.

    @param data_pipe:   The name of the data pipe to reset the minimisation statisics of.  This
                        defaults to the current data pipe.
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
