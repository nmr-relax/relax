###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


class Delete:
    def __init__(self, relax):
        """Class containing functions for reading and writing data."""

        self.relax = relax


    def data(self, run=None, data_type=None):
        """Function for deleting the data out of a file."""

        # Arguments.
        self.run = run
        self.data_type = data_type

        # Test if the sequence data has been read.
        if not len(self.relax.data.res[run]):
            raise RelaxSequenceError

        # Define the different classes of data type.
        valid_types = ['res', 'diff', None]

        # Check the validity of the data type argument.
        if not data_type in valid_types:
            raise RelaxError, "The data type argument " + `data_type` + " is invalid and should be one of " + `valid_types` + "."

        # Check if the run exists and if not, return without deleting anything.
        if not self.run in self.relax.data.run_names:
            return

        # Delete the diffusion data.
        if data_type == 'diff' or data_type == None and self.relax.data.diff.has_key(run):
            del(self.relax.data.diff[run])

        # Delete the residue specific data.
        if data_type == 'res' or data_type == None and self.relax.data.res.has_key(run):
            del(self.relax.data.res[run])

        # Remove the run from 'self.relax.data.run_names' and 'self.relax.data.run_types'.
        self.relax.data.run_names.remove(run)
        self.relax.data.run_types.remove(run)
