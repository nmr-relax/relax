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


class Create_run:
    def __init__(self, relax):
        """Class containing the function for creating a run."""

        self.relax = relax


    def create(self, run=None, run_type=None):
        """Function for creating a run."""

        # Test if the run already exists.
        if run in self.relax.data.run_names:
            raise RelaxRunError, run

        # List of valid run types.
        valid = ['mf']

        # Test if run_type is valid.
        if not run_type in valid:
            raise RelaxError, "The run type name " + `run_type` + " is invalid."

        # Add the run and type.
        self.relax.data.run_names.append(run)
        self.relax.data.run_types.append(run_type)
