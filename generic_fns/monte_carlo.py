###############################################################################
#                                                                             #
# Copyright (C) 2004-2005, 2007-2009 Edward d'Auvergne                        #
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
"""Module for performing Monte Carlo simulations for error analysis."""

# Python module imports.
from copy import deepcopy
from math import sqrt
from random import gauss

# relax module imports.
from generic_fns.mol_res_spin import exists_mol_res_spin_data
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoSequenceError
from specific_fns.setup import get_specific_fn


def create_data(method=None):
    """Function for creating simulation data.

    @keyword method:    The type of Monte Carlo simulation to perform.
    @type method:       str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # Test the method argument.
    valid_methods = ['back_calc', 'direct']
    if method not in valid_methods:
        raise RelaxError("The simulation creation method " + repr(method) + " is not valid.")

    # Specific Monte Carlo data creation, data return, and error return function setup.
    base_data_loop = get_specific_fn('base_data_loop', cdp.pipe_type)
    if method == 'back_calc':
        create_mc_data = get_specific_fn('create_mc_data', cdp.pipe_type)
    return_data = get_specific_fn('return_data', cdp.pipe_type)
    return_error = get_specific_fn('return_error', cdp.pipe_type)
    pack_sim_data = get_specific_fn('pack_sim_data', cdp.pipe_type)

    # Loop over the models.
    for data_index in base_data_loop():
        # Create the Monte Carlo data.
        if method == 'back_calc':
            data = create_mc_data(data_index)

        # Get the original data.
        else:
            data = return_data(data_index)

        # Get the errors.
        error = return_error(data_index)

        # List type data.
        if isinstance(data, list):
            # Loop over the Monte Carlo simulations.
            random = []
            for j in xrange(cdp.sim_number):
                # Randomise the data.
                random.append([])
                for k in xrange(len(data)):
                    # No data or errors.
                    if data[k] == None or error[k] == None:
                        random[j].append(None)
                        continue

                    # Gaussian randomisation.
                    random[j].append(gauss(data[k], error[k]))

        # Dictionary type data.
        if isinstance(data, dict):
            # Loop over the Monte Carlo simulations.
            random = []
            for j in xrange(cdp.sim_number):
                # Randomise the data.
                random.append({})
                for id in data.keys():
                    # No data or errors.
                    if data[id] == None or error[id] == None:
                        random[j][id] = None
                        continue

                    # Gaussian randomisation.
                    random[j][id] = gauss(data[id], error[id])

        # Pack the simulation data.
        pack_sim_data(data_index, random)


def error_analysis(prune=0.0):
    """Function for calculating errors from the Monte Carlo simulations.

    The standard deviation formula used to calculate the errors is the square root of the
    bias-corrected variance, given by the formula::

                   __________________________
                  /   1
        sd  =    /  ----- * sum({Xi - Xav}^2)
               \/   n - 1

    where
        - n is the total number of simulations.
        - Xi is the parameter value for simulation i.
        - Xav is the mean parameter value for all simulations.


    @keyword prune:     The amount to prune the upper and lower tails the distribution.  If set to
                        0.0, no simulations will be pruned.  If set to 1.0, all simulations will be
                        pruned.  This argument should be set 0.0 to avoid meaningless statistics.
    @type prune:        float
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # Model loop, return simulation chi2 array, return selected simulation array, return simulation parameter array, and set error functions.
    model_loop = get_specific_fn('model_loop', cdp.pipe_type)
    if prune > 0.0:
        return_sim_chi2 = get_specific_fn('return_sim_chi2', cdp.pipe_type)
    return_selected_sim = get_specific_fn('return_selected_sim', cdp.pipe_type)
    return_sim_param = get_specific_fn('return_sim_param', cdp.pipe_type)
    set_error = get_specific_fn('set_error', cdp.pipe_type)

    # Loop over the models.
    for model_info in model_loop():
        # Get the selected simulation array.
        select_sim = return_selected_sim(model_info)

        # Initialise an array of indices to prune (an empty array means no pruning).
        indices_to_skip = []

        # Pruning.
        if prune > 0.0:
            # Get the array of simulation chi-squared values.
            chi2_array = return_sim_chi2(model_info)

            # The total number of simulations.
            n = len(chi2_array)

            # Create a sorted array of chi-squared values.
            chi2_sorted = sorted(deepcopy(chi2_array))

            # Number of indices to remove from one side of the chi2 distribution.
            num = int(float(n) * 0.5 * prune)

            # Remove the lower tail.
            for i in xrange(num):
                indices_to_skip.append(chi2_array.index(chi2_sorted[i]))

            # Remove the upper tail.
            for i in xrange(n-num, n):
                indices_to_skip.append(chi2_array.index(chi2_sorted[i]))

        # Loop over the parameters.
        index = 0
        while True:
            # Get the array of simulation parameters for the index.
            param_array = return_sim_param(model_info, index)

            # Break (no more parameters).
            if param_array == None:
                break

            # Simulation parameters with values (ie not None).
            if param_array[0] != None:
                # The total number of simulations.
                n = 0
                for i in xrange(len(param_array)):
                    # Skip deselected simulations.
                    if not select_sim[i]:
                        continue

                    # Prune.
                    if i in indices_to_skip:
                        continue

                    # Increment n.
                    n = n + 1

                # Calculate the sum of the parameter value for all simulations.
                Xsum = 0.0
                for i in xrange(len(param_array)):
                    # Skip deselected simulations.
                    if not select_sim[i]:
                        continue

                    # Prune.
                    if i in indices_to_skip:
                        continue

                    # Sum.
                    Xsum = Xsum + param_array[i]

                # Calculate the mean parameter value for all simulations.
                if n == 0:
                    Xav = 0.0
                else:
                    Xav = Xsum / float(n)

                # Calculate the sum part of the standard deviation.
                sd = 0.0
                for i in xrange(len(param_array)):
                    # Skip deselected simulations.
                    if not select_sim[i]:
                        continue

                    # Prune.
                    if i in indices_to_skip:
                        continue

                    # Sum.
                    sd = sd + (param_array[i] - Xav)**2

                # Calculate the standard deviation.
                if n <= 1:
                    sd = 0.0
                else:
                    sd = sqrt(sd / (float(n) - 1.0))

            # Simulation parameters with the value None.
            else:
                sd = None

            # Set the parameter error.
            set_error(model_info, index, sd)

            # Increment the parameter index.
            index = index + 1


def initial_values():
    """Set the initial simulation parameter values."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # Specific initial Monte Carlo parameter value function setup.
    init_sim_values = get_specific_fn('init_sim_values', cdp.pipe_type)

    # Set the initial parameter values.
    init_sim_values()


def off():
    """Turn simulations off."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # Turn simulations off.
    cdp.sim_state = False


def on():
    """Turn simulations on."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # Turn simulations on.
    cdp.sim_state = True


def select_all_sims(number=None, all_select_sim=None):
    """Set the select flag of all simulations of all models to one.

    @keyword number:            The number of Monte Carlo simulations to set up.
    @type number:               int
    @keyword all_select_sim:    The selection status of the Monte Carlo simulations.  The first
                                dimension of this matrix corresponds to the simulation and the
                                second corresponds to the models.
    @type all_select_sim:       list of lists of bool
    """

    # Model loop and set the selected simulation array functions.
    model_loop = get_specific_fn('model_loop', cdp.pipe_type)
    set_selected_sim = get_specific_fn('set_selected_sim', cdp.pipe_type)

    # Create the selected simulation array with all simulations selected.
    if all_select_sim == None:
        select_sim = [True]*number

    # Loop over the models.
    i = 0
    for model_info in model_loop():
        # Set up the selected simulation array.
        if all_select_sim != None:
            select_sim = all_select_sim[i]

        # Set the selected simulation array.
        set_selected_sim(model_info, select_sim)

        # Model index.
        i = i + 1


def setup(number=None, all_select_sim=None):
    """Function for setting up Monte Carlo simulations.

    @keyword number:            The number of Monte Carlo simulations to set up.
    @type number:               int
    @keyword all_select_sim:    The selection status of the Monte Carlo simulations.  The first
                                dimension of this matrix corresponds to the simulation and the
                                second corresponds to the instance.
    @type all_select_sim:       list of lists of bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if Monte Carlo simulations have already been set up.
    if hasattr(cdp, 'sim_number'):
        raise RelaxError("Monte Carlo simulations have already been set up.")

    # Create a number of MC sim data structures.
    cdp.sim_number = number
    cdp.sim_state = True

    # Select all simulations.
    select_all_sims(number=number, all_select_sim=all_select_sim)
