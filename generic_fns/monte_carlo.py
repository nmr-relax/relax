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


    def initial_values(self, run):
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
