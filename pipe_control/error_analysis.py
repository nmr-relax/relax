###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""Module for performing Monte Carlo simulations for error analysis."""

# Python module imports.
from numpy import diag, ndarray, sqrt
from random import gauss

# relax module imports.
from lib import statistics
from lib.errors import RelaxError
from pipe_control import pipes
from specific_analyses.api import return_api


def covariance_matrix(epsrel=0.0, verbosity=2):
    """Estimate model parameter errors via the covariance matrix technique.

    Note that the covariance matrix error estimate is always of lower quality than Monte Carlo simulations.


    @param epsrel:          Any columns of R which satisfy |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix, where the corresponding rows and columns of the covariance matrix are set to zero.
    @type epsrel:           float
    @keyword verbosity:     The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:        int
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The specific analysis API object.
    api = return_api()

    # Loop over the models.
    for model_info in api.model_loop():
        # Get the Jacobian and weighting matrix.
        jacobian, weights = api.covariance_matrix(model_info=model_info, verbosity=verbosity)

        # Calculate the covariance matrix.
        pcov = statistics.multifit_covar(J=jacobian, weights=weights)

        # To compute one standard deviation errors on the parameters, take the square root of the diagonal covariance.
        sd = sqrt(diag(pcov))

        # Loop over the parameters.
        index = 0
        for name in api.get_param_names():
            # Set the parameter error.
            api.set_error(index, sd[index], model_info=model_info)

            # Increment the parameter index.
            index = index + 1


def monte_carlo_create_data(method=None):
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

    # The specific analysis API object.
    api = return_api()

    # Loop over the models.
    for data_index in api.base_data_loop():
        # Create the Monte Carlo data.
        if method == 'back_calc':
            data = api.create_mc_data(data_index)

        # Get the original data.
        else:
            data = api.return_data(data_index)

        # No data, so skip.
        if data == None:
            continue

        # Get the errors.
        error = api.return_error(data_index)

        # List type data.
        if isinstance(data, list) or isinstance(data, ndarray):
            # Loop over the Monte Carlo simulations.
            random = []
            for j in range(cdp.sim_number):
                # Randomise the data.
                random.append([])
                for k in range(len(data)):
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
            for j in range(cdp.sim_number):
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
        api.sim_pack_data(data_index, random)


def monte_carlo_error_analysis():
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
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # The specific analysis API object.
    api = return_api()

    # Loop over the models.
    for model_info in api.model_loop():
        # Get the selected simulation array.
        select_sim = api.sim_return_selected(model_info=model_info)

        # Loop over the parameters.
        index = 0
        while True:
            # Get the array of simulation parameters for the index.
            param_array = api.sim_return_param(index, model_info=model_info)

            # Break (no more parameters).
            if param_array == None:
                break

            # Handle dictionary type parameters.
            if isinstance(param_array[0], dict):
                # Initialise the standard deviation structure as a dictionary.
                sd = {}

                # Loop over each key.
                for key in param_array[0].keys():
                    # Create a list of the values for the current key.
                    data = []
                    for i in range(len(param_array)):
                        data.append(param_array[i][key])

                    # Calculate and store the SD.
                    sd[key] = statistics.std(values=data, skip=select_sim)

            # Handle list type parameters.
            elif isinstance(param_array[0], list):
                # Initialise the standard deviation structure as a list.
                sd = []

                # Loop over each element.
                for j in range(len(param_array[0])):
                    # Create a list of the values for the current key.
                    data = []
                    for i in range(len(param_array)):
                        data.append(param_array[i][j])

                    # Calculate and store the SD.
                    sd.append(statistics.std(values=data, skip=select_sim))

             # SD of simulation parameters with values (ie not None).
            elif param_array[0] != None:
                sd = statistics.std(values=param_array, skip=select_sim)

            # Simulation parameters with the value None.
            else:
                sd = None

            # Set the parameter error.
            api.set_error(index, sd, model_info=model_info)

            # Increment the parameter index.
            index = index + 1

    # Turn off the Monte Carlo simulation state, as the MC analysis is now finished.
    cdp.sim_state = False


def monte_carlo_initial_values():
    """Set the initial simulation parameter values."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # The specific analysis API object.
    api = return_api()

    # Set the initial parameter values.
    api.sim_init_values()


def monte_carlo_off():
    """Turn simulations off."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # Turn simulations off.
    cdp.sim_state = False


def monte_carlo_on():
    """Turn simulations on."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test if simulations have been set up.
    if not hasattr(cdp, 'sim_state'):
        raise RelaxError("Monte Carlo simulations have not been set up.")

    # Turn simulations on.
    cdp.sim_state = True


def monte_carlo_select_all_sims(number=None, all_select_sim=None):
    """Set the select flag of all simulations of all models to one.

    @keyword number:            The number of Monte Carlo simulations to set up.
    @type number:               int
    @keyword all_select_sim:    The selection status of the Monte Carlo simulations.  The first
                                dimension of this matrix corresponds to the simulation and the
                                second corresponds to the models.
    @type all_select_sim:       list of lists of bool
    """

    # The specific analysis API object.
    api = return_api()

    # Create the selected simulation array with all simulations selected.
    if all_select_sim == None:
        select_sim = [True]*number

    # Loop over the models.
    i = 0
    for model_info in api.model_loop():
        # Skip function.
        if api.skip_function(model_info=model_info):
            continue

        # Set up the selected simulation array.
        if all_select_sim != None:
            select_sim = all_select_sim[i]

        # Set the selected simulation array.
        api.set_selected_sim(select_sim, model_info=model_info)

        # Model index.
        i += 1


def monte_carlo_setup(number=None, all_select_sim=None):
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

    # Create a number of MC sim data structures.
    cdp.sim_number = number
    cdp.sim_state = True

    # Select all simulations.
    monte_carlo_select_all_sims(number=number, all_select_sim=all_select_sim)
