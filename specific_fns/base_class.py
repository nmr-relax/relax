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


class Common_functions:
    def __init__(self):
        """Base class containing functions common to the specific functions."""


    def initialise_data(self, data, run, sim=0, err=0):
        """Function for the initialisation of data structures.

        Only data structures which do not exist are created.
        """

        # Get the data names.
        data_names = self.data_names()

        # Standard data structures.
        if not sim and not err:
            for name in data_names:
                # If the name is not in 'data', add it.
                if not hasattr(data, name):
                    setattr(data, name, self.data_init(name))

        # Simulation data structures.
        if sim:
            for name in data_names:
                # Add '_sim' to the names.
                name = name + '_sim'

                # If the name is not in 'data', add it.
                if not hasattr(data, name):
                    setattr(data, name, self.data_init(name))

        # Error data structures.
        if err:
            for name in data_names:
                # Add '_sim' to the names.
                name = name + '_sim'

                # If the name is not in 'data', add it.
                if not hasattr(data, name):
                    setattr(data, name, self.data_init(name))


    def return_data(self, run, i):
        """Function for returning the Ri data structure."""

        return self.relax.data.res[run][i].relax_data


    def return_error(self, run, i):
        """Function for returning the Ri error structure."""

        return self.relax.data.res[run][i].relax_error


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(self.relax.data.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        self.relax.data.res[run][i].relax_sim_data = sim_data
