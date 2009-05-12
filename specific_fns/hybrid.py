###############################################################################
#                                                                             #
# Copyright (C) 2006-2009 Edward d'Auvergne                                   #
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
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data
from generic_fns.sequence import compare_sequence
from relax_errors import RelaxError, RelaxNoSequenceError, RelaxPipeError, RelaxSequenceError


class Hybrid:
    def __init__(self):
        """Class containing function specific to hybrid models."""


    def duplicate_data(self, pipe_from=None, pipe_to=None):
        """Duplicate the data specific to a single hybrid data pipe.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        """

        # First create the pipe_to data pipe, if it doesn't exist, but don't switch to it.
        if not pipes.has_pipe(pipe_to):
            pipes.create(pipe_to, pipe_type='hybrid', switch=False)

        # Get the data pipes.
        dp_from = pipes.get_pipe(pipe_from)
        dp_to = pipes.get_pipe(pipe_to)

        # Test that the target data pipe has no sequence loaded.
        if not exists_mol_res_spin_data(pipe_to):
            raise RelaxSequenceError, pipe_to

        # Duplicate the hybrid pipe list data structure.
        dp_to.hybrid_pipes = dp_from.hybrid_pipes


    def hybridise(self, hybrid=None, pipe_list=None):
        """Create the hybrid data pipe.

        @keyword hybrid:    The name of the new hybrid data pipe.
        @type hybrid:       str
        @keyword pipe_list: The list of data pipes that the hybrid is composed of.
        @type pipe_list:    list of str
        """

        # Test if the hybrid data pipe already exists.
        if hybrid in pipes.pipe_names():
            raise RelaxPipeError, hybrid

        # Loop over the pipes to be hybridised and check them.
        pipe_type = pipes.get_type(pipe_list[0])
        for pipe in pipe_list:
            # Switch to the data pipe.
            pipes.switch(pipe)

            # Test if the pipe exists.
            pipes.test()

            # Check that the pipe types match.
            if pipes.get_type() != pipe_type:
                raise RelaxError, "The data pipe types do not match."

            # Test if sequence data is loaded.
            if not exists_mol_res_spin_data():
                raise RelaxNoSequenceError

        # Check that the sequence data matches in all pipes.
        for i in range(1, len(pipe_list)):
            compare_sequence(pipe_list[0], pipe_list[1])

        # Create the data pipe.
        pipes.create(pipe_name=hybrid, pipe_type='hybrid')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Store the pipe list forming the hybrid.
        cdp.hybrid_pipes = pipe_list


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

