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

        # Test if the run exists.
        if not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Run argument.
        if run == None:
            self.runs = self.relax.data.run_names
        else:
            self.runs = [run]

        # Data type argument.
        self.data_type = data_type

        # Define the different classes of data type.
        global_types = ['res', 'diff', None]
        specific_types = ['relax_data', 'mf']

        # Check the validity of the data type argument.
        if not self.data_type in global_types and not self.data_type in specific_types:
            raise RelaxError, "The data type argument " + `self.data_type` + " is invalid and should be one of either " + `global_types` + " or " + `specific_types` + "."

        # Delete the global data types.
        if self.data_type in global_types:
            self.delete_global_types()

        # Delete the residue specific data types.
        elif self.data_type in specific_types:
            # Specific data names function setup.
            self.data_names = self.relax.specific_setup.setup('data_names', data_type)

            # Delete function.
            self.delete_specific_types()

        # Clean up the runs, ie delete any runs for which there is no data left.
        self.clean_runs()


    def clean_runs(self):
        """Function for deleting any runs for which there is no data left."""

        # An array of runs to retain.
        keep_runs = []

        # Find out if any data in 'self.relax.data' is assigned to a run.
        for name in dir(self.relax.data):
            # Get the data and check that it is a dictionary.
            object = getattr(self.relax.data, name)
            if not hasattr(object, 'keys'):
                continue

            # Add the keys to 'keep_runs'.
            for key in object.keys():
                if not key in keep_runs:
                    keep_runs.append(key)

        # Delete the runs in 'self.relax.data.run_names' and 'self.relax.data.run_types' which are not in 'keep_runs'.
        for run in self.relax.data.run_names:
            if not run in keep_runs:
                # Index.
                index = self.relax.data.run_names.index(run)

                # Remove from run_names.
                self.relax.data.run_names.remove(run)

                # Remove from run_types.
                temp = self.relax.data.run_types.pop(index)


    def delete_global_types(self):
        """Function for deleting global data types."""

        # Loop over the runs.
        for run in self.runs:
            # Delete the diffusion data.
            if self.data_type == 'diff' or (self.data_type == None and self.relax.data.diff.has_key(run)):
                del(self.relax.data.diff[run])

            # Delete the residue specific data.
            if self.data_type == 'res' or (self.data_type == None and self.relax.data.res.has_key(run)):
                del(self.relax.data.res[run])


    def delete_specific_types(self):
        """Function for deleting residue specific data types."""

        # Get the data names.
        names = self.data_names()

        # Loop over the runs.
        for run in self.runs:
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[run])):
                for name in names:
                    # Skip if 'name' is not in 'data'.
                    if not hasattr(self.relax.data.res[run][i], name):
                        continue

                    # Delete the data.
                    delattr(self.relax.data.res[run][i], name)
