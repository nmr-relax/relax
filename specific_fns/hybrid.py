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

# Python module imports.
from warnings import warn

# relax module imports.
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data
from generic_fns.sequence import compare_sequence
from relax_errors import RelaxError, RelaxNoSequenceError, RelaxPipeError, RelaxSequenceError
import setup
from relax_warnings import RelaxDeselectWarning


class Hybrid:
    """Class containing function specific to hybrid models."""

    def _hybridise(self, hybrid=None, pipe_list=None):
        """Create the hybrid data pipe.

        @keyword hybrid:    The name of the new hybrid data pipe.
        @type hybrid:       str
        @keyword pipe_list: The list of data pipes that the hybrid is composed of.
        @type pipe_list:    list of str
        """

        # Test if the hybrid data pipe already exists.
        if hybrid in pipes.pipe_names():
            raise RelaxPipeError(hybrid)

        # Loop over the pipes to be hybridised and check them.
        pipe_type = pipes.get_type(pipe_list[0])
        for pipe in pipe_list:
            # Switch to the data pipe.
            pipes.switch(pipe)

            # Test if the pipe exists.
            pipes.test()

            # Check that the pipe types match.
            if pipes.get_type() != pipe_type:
                raise RelaxError("The data pipe types do not match.")

            # Test if sequence data is loaded.
            if not exists_mol_res_spin_data():
                raise RelaxNoSequenceError

        # Check that the sequence data matches in all pipes.
        for i in range(1, len(pipe_list)):
            compare_sequence(pipe_list[0], pipe_list[1])

        # Create the data pipe.
        pipes.create(pipe_name=hybrid, pipe_type='hybrid')

        # Store the pipe list forming the hybrid.
        cdp.hybrid_pipes = pipe_list


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single hybrid data pipe.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @keyword model_info:    The model information from model_info().
        @type model_info:       int
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       A flag which if True will cause info to be printed out.
        @type verbose:          bool
        """

        # First create the pipe_to data pipe, if it doesn't exist, but don't switch to it.
        if not pipes.has_pipe(pipe_to):
            pipes.create(pipe_to, pipe_type='hybrid', switch=False)

        # Get the data pipes.
        dp_from = pipes.get_pipe(pipe_from)
        dp_to = pipes.get_pipe(pipe_to)

        # Test that the target data pipe has no sequence loaded.
        if not exists_mol_res_spin_data(pipe_to):
            raise RelaxSequenceError(pipe_to)

        # Duplicate the hybrid pipe list data structure.
        dp_to.hybrid_pipes = dp_from.hybrid_pipes


    def model_desc(self, model_info):
        """Return a description of the model.

        @param model_info:  The model information from the model_loop().  This is unused.
        @type model_info:   int
        @return:            The model description.
        @rtype:             str
        """

        return "hybrid model"


    def model_loop(self):
        """Dummy generator method - this should be a global model!"""

        yield 0


    def model_type(self):
        """Method stating that this is a global model."""

        return 'global'


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics of the hybrid.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_index:   The model index.  This is zero for the global models or equal to the
                                global spin index (which covers the molecule, residue, and spin
                                indices).  This originates from the model_loop().
        @type model_index:      int
        @keyword spin_id:       The spin identification string.  Either this or the instance keyword
                                argument must be supplied.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are
                                returned.  If None, then the appropriateness of global or local
                                statistics is automatically determined.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of
                                parameters (k), the number of data points (n), and the chi-squared
                                value (chi2).
        @rtype:                 tuple of int, int, float
        """

        # Bad argument combination.
        if model_info == None and spin_id == None:
            raise RelaxError("Either the model_info or spin_id argument must be supplied.")
        elif model_info != None and spin_id != None:
            raise RelaxError("The model_info arg " + repr(model_info) + " and spin_id arg " + repr(spin_id) + " clash.  Only one should be supplied.")

        # Initialise.
        k_total = 0
        n_total = 0
        chi2_total = 0.0

        # Specific setup.
        for pipe in cdp.hybrid_pipes:
            # Switch to the data pipe.
            pipes.switch(pipe)

            # Specific model statistics and number of instances functions.
            model_statistics = setup.get_specific_fn('model_stats', pipes.get_type(pipe))

            # Loop over the instances.
            #for i in xrange(num):
            # Get the statistics.
            k, n, chi2 = model_statistics(model_info=model_info, spin_id=spin_id, global_stats=global_stats)

            # Bad stats.
            if k == None or n == None or chi2 == None:
                continue

            # Sum the stats.
            k_total = k_total + k
            n_total = n_total + n
            chi2_total = chi2_total + chi2

        # Return the totals.
        return k_total, n_total, chi2_total


    def num_instances(self):
        """Return the number of instances, which for hybrids is always 1.

        @return:    The number of instances.
        @rtype:     int
        """

        return 1


    def skip_function(self, model_info):
        """Dummy function.

        @param model_info:  The model index from model_loop().
        @type model_info:   int
        @return:            True if the data should be skipped, False otherwise.
        @rtype:             bool
        """

        # Don't skip data.
        return False

