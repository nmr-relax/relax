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


class Monte_carlo:
    def __init__(self, relax):
        """Class containing functions for Monte Carlo simulations."""

        self.relax = relax


    def create_data(self, run=None, method=None):
        """Function for creating simulation data."""

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Test the method argument.
        valid_methods = ['back_calc', 'direct']
        if method not in valid_methods:
            raise RelaxError, "The method " + `method` + " is not valid."


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
