###############################################################################
#                                                                             #
# Copyright (C) 2006-2007 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import RelaxError, RelaxNoPipeError, RelaxNoSequenceError, RelaxPipeError, RelaxSequenceError


class Hybrid:
    def __init__(self):
        """Class containing function specific to hybrid models."""


    def duplicate_data(self, new_run=None, old_run=None, instance=None):
        """Function for duplicating data."""

        # Test that the new run exists.
        if not new_run in ds.run_names:
            raise RelaxNoPipeError, new_run

        # Test that the old run exists.
        if not old_run in ds.run_names:
            raise RelaxNoPipeError, old_run

        # Test that the new run has no sequence loaded.
        if ds.res.has_key(new_run):
            raise RelaxSequenceError, new_run

        # Reset the new run type to hybrid!
        ds.run_types[ds.run_names.index(new_run)] = 'hybrid'

        # Duplicate the hybrid run data structure.
        ds.hybrid_pipes[new_run] = ds.hybrid_pipes[old_run]


    def hybridise(self, hybrid=None, runs=None):
        """Function for creating the hybrid run."""

        # Test if the hybrid run already exists.
        if hybrid in ds.run_names:
            raise RelaxPipeError, hybrid

        # Loop over the runs to be hybridised.
        for run in runs:
            # Test if the current pipe exists.
            pipes.test()

            # Test if sequence data is loaded.
            if not ds.res.has_key(run):
                raise RelaxNoSequenceError, run

        # Check the sequence.
        for i in xrange(len(ds.res[runs[0]])):
            # Reassign the data structure.
            data1 = ds.res[runs[0]][i]

            # Loop over the rest of the runs.
            for run in runs[1:]:
                # Reassign the data structure.
                data2 = ds.res[run][i]

                # Test if the sequence is the same.
                if data1.name != data2.name or data1.num != data2.num:
                    raise RelaxError, "The residues '" + data1.name + " " + `data1.num` + "' of the run " + `runs[0]` + " and '" + data2.name + " " + `data2.num` + "' of the run " + `run` + " are not the same."

        # Add the run and type to the runs list.
        ds.run_names.append(hybrid)
        ds.run_types.append('hybrid')

        # Create the data structure of the runs which form the hybrid.
        ds.hybrid_pipes[hybrid] = runs


    def model_statistics(self, run=None, instance=None, global_stats=None):
        """Function for returning the values k, n, and chi2 of the hybrid.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.
        """

        # Arguments.
        self.run = run

        # Initialise.
        k_total = 0
        n_total = 0
        chi2_total = 0.0

        # Specific setup.
        for run in ds.hybrid_pipes[self.run]:
            # Function type.
            function_type = ds.run_types[ds.run_names.index(run)]

            # Specific model statistics and number of instances functions.
            model_statistics = self.relax.specific_setup.setup('model_stats', function_type)

            # Loop over the instances.
            for i in xrange(num):
                # Get the statistics.
                k, n, chi2 = model_statistics(run, instance=i, global_stats=global_stats)

                # Bad stats.
                if k == None or n == None or chi2 == None:
                    continue

                # Sum the stats.
                k_total = k_total + k
                n_total = n_total + n
                chi2_total = chi2_total + chi2

        # Return the totals.
        return k_total, n_total, chi2_total


    def num_instances(self, run=None):
        """Function for returning the number of instances, which for hybrids is always 1."""

        return 1


    def skip_function(self, run=None, instance=None, min_instances=None, num_instances=None):
        """Dummy function."""

        return

