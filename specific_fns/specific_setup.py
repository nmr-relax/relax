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


from re import match


class Specific_setup:
    def __init__(self, relax):
        """Class for equation type specific function setup."""

        self.relax = relax


    def setup(self, function_type, eqi, raise_error=1):
        """Setup function."""

        # Initialise.
        self.function_type = function_type

        # Sequence data.
        if match('seq', eqi):
            function = self.seq_funcs()

        # Diffusion tensor.
        elif match('diff', eqi):
            function = self.diff_funcs()

        # Relaxation data.
        elif match('relax_data', eqi):
            function = self.relax_funcs()

        # Model-free analysis.
        elif eqi == 'mf':
            function = self.mf_funcs()

        # Raise an error if the function doesn't exist.
        if raise_error:
            if function == None:
                raise RelaxFuncSetupError, (eqi, function_type)

        # Return the function.
        return function


    def diff_funcs(self):
        """Diffusion tensor specific functions."""

        # Data names function.
        if self.function_type == 'data_names':
            return self.relax.generic.diffusion_tensor.data_names


    def mf_funcs(self):
        """Model-free analysis specific functions."""

        # Calculate function.
        if self.function_type == 'calculate':
            return self.relax.specific.model_free.calculate

        # Data names function.
        if self.function_type == 'data_names':
            return self.relax.specific.model_free.data_names

        # Duplicate data.
        if self.function_type == 'duplicate_data':
            return self.relax.specific.model_free.duplicate_data

        # Grid search function.
        if self.function_type == 'grid_search':
            return self.relax.specific.model_free.grid_search

        # Map labels.
        if self.function_type == 'map_labels':
            return self.relax.specific.model_free.map_labels

        # Map bounds function.
        if self.function_type == 'map_bounds':
            return self.relax.specific.model_free.map_bounds

        # Minimise function.
        if self.function_type == 'minimise':
            return self.relax.specific.model_free.minimise

        # Model statistics.
        if self.function_type == 'model_stats':
            return self.relax.specific.model_free.model_stats

        # Number of instances.
        if self.function_type == 'num_instances':
            return self.relax.specific.model_free.num_instances

        # Read results file function.
        if self.function_type == 'read':
            return self.relax.specific.model_free.read_results

        # Set function.
        if self.function_type == 'set':
            return self.relax.specific.model_free.set

        # Skip function.
        if self.function_type == 'skip_function':
            return self.relax.specific.model_free.skip_function

        # Write header function.
        if self.function_type == 'write_header':
            return self.relax.specific.model_free.write_header

        # Write results function.
        if self.function_type == 'write_results':
            return self.relax.specific.model_free.write_results


    def relax_funcs(self):
        """Relaxation curve fitting functions."""

        # Data names function.
        if self.function_type == 'data_names':
            return self.relax.specific.relax_data.data_names


    def seq_funcs(self):
        """Sequence specific functions."""

        # Data names function.
        if self.function_type == 'data_names':
            return self.relax.generic.sequence.data_names
