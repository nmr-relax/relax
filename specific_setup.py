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


    def setup(self, function_type, eqi):
        """Setup function."""

        # Initialise.
        self.function_type = function_type
        self.eqi = eqi

        # Sequence data.
        if match('seq', eqi):
            if match('data_names', function_type):
                return self.relax.sequence.data_names

        # Diffusion tensor.
        elif match('diff', eqi):
            if match('data_names', function_type):
                return self.relax.diffusion_tensor.data_names

        # Relaxation data.
        elif match('relax_data', eqi):
            if match('data_names', function_type):
                return self.relax.relax_data.data_names

        # Model-free analysis.
        elif eqi == 'mf':
            return self.mf_funcs()

            #if match('calc', function_type):
            #    return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.calculate
            #if match('data_names', function_type):
            #    return self.relax.model_free.data_names
            #if match('fixed', function_type):
            #    return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.fixed_setup, self.relax.model_free.minimise
            #if match('grid_search', function_type):
            #    return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.grid_setup, self.relax.model_free.minimise
            #if match('map_labels', function_type):
            #    return self.relax.model_free.map_labels
            #if match('map_space', function_type):
            #    return self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.map_bounds, self.relax.model_free.minimise
            #if match('minimise', function_type):
            #    return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.minimise
            #if match('read', function_type):
            #    return self.relax.model_free.read_results
            #if match('write', function_type):
            #    return self.relax.model_free.write_header, self.relax.model_free.write_results


    def mf_funcs(self):
        """Model-free analysis specific functions."""

        # Calculate function.
        if self.function_type == 'calc':
            return self.relax.model_free.calculate

        # Delete function.
        if self.function_type == 'data_names':
            return self.relax.model_free.data_names

        # Fixed setup function.
        if self.function_type == 'fixed':
            return self.relax.model_free.fixed_setup

        # Grid setup function.
        if self.function_type == 'grid_search':
            return self.relax.model_free.grid_setup

        # Map labels.
        if self.function_type == 'map_labels':
            return self.relax.model_free.map_labels

        # Map bounds function.
        if self.function_type == 'map_bounds':
            return self.relax.model_free.map_bounds

        # Minimise function.
        if self.function_type == 'minimise':
            return self.relax.model_free.minimise

        # Parameter vector.
        if self.function_type == 'param_vector':
            return self.relax.model_free.assemble_param_vector

        # Read results file function.
        if self.function_type == 'read':
            return self.relax.model_free.read_results

        # Scaling matrix.
        if self.function_type == 'scaling_matrix':
            return self.relax.model_free.assemble_scaling_matrix

        # Write header function.
        if self.function_type == 'write_header':
            return self.relax.model_free.write_header

        # Write results function.
        if self.function_type == 'write_results':
            return self.relax.model_free.write_results
