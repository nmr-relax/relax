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
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Define the different classes of data type.
        global_types = ['seq', 'diff']
        sequence_types = ['relax_data', 'mf', 'all']

        # Check the validity of the data type argument.
        if not data_type in global_types and not data_type in sequence_types:
            raise RelaxError, "The data type argument " + `data_type` + " is invalid and should be one of either " + `global_types` + " or " + `sequence_types` + "."

        # Equation type specific function setup.
        self.data_names = self.relax.specific_setup.setup('data_names', data_type)
        if self.data_names == None:
            raise RelaxFuncSetupError, ('data_names', data_type)

        # Delete the global data types.
        if data_type in global_types:
            self.delete_globals()

        # Delete the sequence data types and remove the run.
        else:
            self.delete_seq_types()


    def delete_globals(self):
        """Function for deleting global data types."""

        # Check if the run argument has been supplied.
        if self.run != None:
            raise RelaxError, "When the data type is set to " + `self.data_type` + ", the run argument " + `self.run` + " must be None."

        # Get the data names.
        names = self.data_names()

        # Loop over the names.
        for name in names:
            # Skip over the data if it is not in 'self.relax.data'
            if not hasattr(self.relax.data, name):
                continue

            # Get the data.
            object = getattr(self.relax.data, name)

            # If the data is a list, replace it with an empty list.
            if type(object) == list:
                setattr(self.relax.data, name, [])

            # Delete the data.
            else:
                delattr(self.relax.data, name)


        # Run removal.
        ##############

        # An array of runs to retain.
        keep_runs = []

        # Find out if any data in 'self.relax.data' is assigned to a run.
        for name in dir(self.relax.data):
            # Get the data and check that it is a dictionary.
            object = getattr(self.relax.data, name)
            if type(object) != dict:
                continue

            # Add the keys to 'keep_runs'.
            for key in object.keys():
                if not key in keep_runs:
                    keep_runs.append(key)

        # Find out if any data in 'self.relax.data.res[i]' is assigned to a run.
        for i in xrange(len(self.relax.data.res)):
            for name in dir(self.relax.data.res[i]):
                # Get the data and check that it is a dictionary.
                object = getattr(self.relax.data.res[i], name)
                if type(object) != dict:
                    continue

                # Add the keys to 'keep_runs'.
                for key in object.keys():
                    if not key in keep_runs:
                        keep_runs.append(key)

        # Remove the run from 'self.relax.data.run_names'.
        for run in self.relax.data.run:
            if not run in keep_runs:
                self.relax.data.run_names.remove(run)
                self.relax.data.run_types.remove(run)


    def delete_seq_types(self):
        """Function for deleting residue specific data types."""

        # Check if the run exists and if not, return without deleting anything.
        if self.run == None or not self.run in self.relax.data.run_names:
            return


        # Data removal.
        ###############

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Get the data names.
            names = self.data_names()

            # Loop over the names.
            for name in names:
                # Skip over the data if it is not in 'data'
                if not hasattr(self.relax.data.res[i], name):
                    continue

                # Get the data.
                object = getattr(self.relax.data.res[i], name)

                # Skip over the data if it doesn't contain the run.
                if not object.has_key(self.run):
                    continue

                # Delete the data.
                del(object[self.run])


        # Run removal.
        ##############

        # Find out if any data in 'self.relax.data' is assigned to the run.
        for name in dir(self.relax.data):
            # Get the data and check that it is a dictionary.
            object = getattr(self.relax.data, name)
            if type(object) != dict:
                continue

            # If the data contains the key 'run', exit this function without removing the run from 'self.relax.data.run_names'.
            if object.has_key(self.run):
                return

        # Find out if any data in 'self.relax.data.res[i]' is assigned to the run.
        for i in xrange(len(self.relax.data.res)):
            for name in dir(self.relax.data.res[i]):
                # Get the data and check that it is a dictionary.
                object = getattr(self.relax.data.res[i], name)
                if type(object) != dict:
                    continue

                # If the data contains the key 'run', exit this function without removing the run from 'self.relax.data.run_names'.
                if object.has_key(self.run):
                    return

        # Remove the run from 'self.relax.data.run_names'.
        self.relax.data.run_names.remove(self.run)
        self.relax.data.run_types.remove(self.run)
