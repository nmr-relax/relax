###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

from copy import deepcopy
from math import sqrt
from random import gauss


class Monte_carlo:
    def __init__(self, relax):
        """Class containing functions for Monte Carlo simulations."""

        self.relax = relax


    def create_data(self, run=None, method=None):
        """Function for creating simulation data.

        It is assumed that all data types are residue specific.
        """

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `run` + " have not been set up."

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Test the method argument.
        valid_methods = ['back_calc', 'direct']
        if method not in valid_methods:
            raise RelaxError, "The method " + `method` + " is not valid."

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific Monte Carlo data creation, data return, and error return function setup.
        create_mc_data = self.relax.specific_setup.setup('create_mc_data', function_type)
        return_data = self.relax.specific_setup.setup('return_data', function_type)
        return_error = self.relax.specific_setup.setup('return_error', function_type)
        pack_sim_data = self.relax.specific_setup.setup('pack_sim_data', function_type)

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Skip unselected residues.
            if not self.relax.data.res[run][i].select:
                continue

            # Create the Monte Carlo data.
            if method == 'back_calc':
                data = create_mc_data(run, i)

            # Get the original data.
            else:
                data = return_data(run, i)

            # Get the errors.
            error = return_error(run, i)

            # Loop over the Monte Carlo simulations.
            random = []
            for j in xrange(self.relax.data.sim_number[run]):
                # Randomise the data.
                random.append([])
                for k in xrange(len(data)):
                    random[j].append(gauss(data[k], error[k]))

            # Pack the simulation data.
            pack_sim_data(run, i, random)


    def error_analysis(self, run=None, prune=0):
        """Function for calculating errors from the Monte Carlo simulations.

        The standard deviation formula used to calculate the errors is the square root of the
        bias-corrected variance, given by the formula:

                       ____________________________
                      /   1
            sd  =    /  ----- * sum({Xi - Xav}^2)]
                   \/   n - 1

        where:
            n is the total number of simulations.
            Xi is the parameter value for simulation i.
            Xav is the mean parameter value for all simulations.
        """

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `run` + " have not been set up."

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific number of instances, return simulation chi2 array, return simulation parameter array, and set error functions.
        count_num_instances = self.relax.specific_setup.setup('num_instances', function_type)
        if prune > 0.0:
            return_sim_chi2 = self.relax.specific_setup.setup('return_sim_chi2', function_type)
        return_sim_param = self.relax.specific_setup.setup('return_sim_param', function_type)
        set_error = self.relax.specific_setup.setup('set_error', function_type)

        # Count the number of instances.
        num_instances = count_num_instances(run)

        # Loop over the instances.
        for instance in xrange(num_instances):
            # Initialise an array of indecies to prune.
            indecies_to_skip = []

            # Pruning.
            if prune > 0.0:
                # Get the array of simulation chi-squared values.
                chi2_array = return_sim_chi2(run, instance)

                # The total number of simulations.
                n = len(chi2_array)

                # Create a sorted array of chi-squared values.
                chi2_sorted = deepcopy(chi2_array)
                chi2_sorted.sort()

                # Number of indecies to remove from one side of the chi2 distribution.
                num = int(float(n) * 0.5 * prune)

                # Remove the lower tail.
                for i in xrange(num):
                    indecies_to_skip.append(chi2_array.index(chi2_sorted[i]))

                # Remove the upper tail.
                for i in xrange(n-num, n):
                    indecies_to_skip.append(chi2_array.index(chi2_sorted[i]))

            # Loop over the parameters.
            index = 0
            while 1:
                # Get the array of simulation parameters for the index.
                param_array = return_sim_param(run, instance, index)

                # Break (no more parameters).
                if param_array == None:
                    break

                # Simulation parameters with values (ie not None).
                if param_array[0] != None:
                    # The total number of simulations.
                    n = len(param_array)

                    # Calculate the mean parameter value for all simulations.
                    Xav = 0.0
                    for i in xrange(n):
                        # Prune.
                        if i in indecies_to_skip:
                            continue

                        # Sum.
                        Xav = Xav + param_array[i]
                    Xav = Xav / (float(n) - float(len(indecies_to_skip)))

                    # Calculate the sum part of the standard deviation.
                    sd = 0.0
                    for i in xrange(n):
                        # Prune.
                        if i in indecies_to_skip:
                            continue

                        # Sum.
                        sd = sd + (param_array[i] - Xav)**2

                    # Calculate the standard deviation.
                    sd = sqrt(sd / (float(n) - float(len(indecies_to_skip)) - 1.0))

                # Simulation parameters with the value None.
                else:
                    sd = None

                # Set the parameter error.
                set_error(run, instance, index, sd)

                # Increment the parameter index.
                index = index + 1


    def initial_values(self, run=None):
        """Function for setting the initial simulation parameter values."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `run` + " have not been set up."

        # Function type.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(run)]

        # Specific initial Monte Carlo parameter value function setup.
        init_sim_values = self.relax.specific_setup.setup('init_sim_values', function_type)

        # Set the initial parameter values.
        init_sim_values(run)


    def off(self, run=None):
        """Function for turning simulations off."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `run` + " have not been set up."

        # Turn simulations off.
        self.relax.data.sim_state[run] = 0


    def on(self, run=None):
        """Function for turning simulations on."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if simulations have been set up.
        if not hasattr(self.relax.data, 'sim_state'):
            raise RelaxError, "Monte Carlo simulations for the run " + `run` + " have not been set up."

        # Turn simulations on.
        self.relax.data.sim_state[run] = 1


    def setup(self, run=None, number=0):
        """Function for setting up Monte Carlo simulations."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test if Monte Carlo simulations have already been set up for the given run.
        if hasattr(self.relax.data, 'sim_number') and self.relax.data.sim_number.has_key(run):
            raise RelaxError, "Monte Carlo simulations for the run " + `run` + " have already been set up."

        # Create the data structure 'sim_number' if it doesn't exist.
        if not hasattr(self.relax.data, 'sim_number'):
            self.relax.data.sim_number = {}

        # Add the simulation number.
        self.relax.data.sim_number[run] = number

        # Create the data structure 'sim_state'.
        if not hasattr(self.relax.data, 'sim_state'):
            self.relax.data.sim_state = {}

        # Turn simulations on.
        self.relax.data.sim_state[run] = 1
