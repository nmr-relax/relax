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


    def randomise(self, run=None, number=None, prune=None, method=None):
        """Function for setting up Monte Carlo simulations."""

        # Arguments.
        self.run = run
        self.number = number
        self.prune = prune
        self.method = method

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

