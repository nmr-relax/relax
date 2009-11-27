###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006 Edward d'Auvergne                                  #
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


class Runs:
    def __init__(self, relax):
        """Class containing the function for creating a run."""

        self.relax = relax


    def create(self, run=None, run_type=None):
        """Function for creating a run."""

        # Test if the run already exists.
        if run in self.relax.data.run_names:
            raise RelaxRunError, run

        # List of valid run types.
        valid = ['jw', 'mf', 'mf_csa', 'noe', 'relax_fit', 'srls']

        # Test if run_type is valid.
        if not run_type in valid:
            raise RelaxError, "The run type name " + `run_type` + " is invalid and must be one of the strings in the list " + `valid` + "."

        # Test that the C modules have been loaded.
        if run_type == 'relax_fit' and not C_module_exp_fn:
            raise RelaxError, "Relaxation curve fitting is not availible.  Try compiling the C modules on your platform."

        # Add the run and type.
        self.relax.data.run_names.append(run)
        self.relax.data.run_types.append(run_type)


    def delete(self, run=None):
        """Function for deleting a run."""

        # Test if the run exists.
        if run != None and not run in self.relax.data.run_names:
            raise RelaxNoRunError, run

        # Find out if any data in 'self.relax.data' is assigned to a run.
        for name in dir(self.relax.data):
            # Get the object.
            object = getattr(self.relax.data, name)

            # Skip to the next data structure if the object is not a dictionary.
            if not hasattr(object, 'keys'):
                continue

            # Delete the data if the object contains the key 'run'.
            if object.has_key(run):
                del(object[run])

        # Clean up the runs, ie delete any runs for which there is no data left.
        self.eliminate_unused_runs()


    def eliminate_unused_runs(self):
        """Function for eliminating any runs for which there is no data."""

        # An array of runs to retain.
        keep_runs = []

        # Find out if any data in 'self.relax.data' is assigned to a run.
        for name in dir(self.relax.data):
            # Skip to the next data structure if the object is not a dictionary.
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


    def list_of_runs(self, run):
        """Function for creating a list of runs."""

        # All runs.
        if run == None:
            runs = deepcopy(self.relax.data.run_names)

        # Single run.
        elif type(run) == str:
            runs = [run]

        # List of runs.
        else:
            runs = run

        # Return the list.
        return runs
