###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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

        # Sequence data.
        if match('seq', eqi):
            if match('delete', function_type):
                return self.relax.sequence.data_names

        # Diffusion tensor.
        elif match('diff', eqi):
            if match('delete', function_type):
                return self.relax.diffusion_tensor.data_names

        # Relaxation data.
        elif match('relax_data', eqi):
            if match('delete', function_type):
                return self.relax.relax_data.data_names

        # Model-free analysis.
        elif match('mf', eqi):
            if match('calc', function_type):
                return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.calculate
            if match('delete', function_type):
                return self.relax.model_free.data_names
            if match('fixed', function_type):
                return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.fixed_setup, self.relax.model_free.minimise
            if match('grid_search', function_type):
                return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.grid_setup, self.relax.model_free.minimise
            if match('map_labels', function_type):
                return self.relax.model_free.map_labels
            if match('map_space', function_type):
                return self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.map_bounds, self.relax.model_free.minimise
            if match('minimise', function_type):
                return self.relax.model_free.assemble_param_vector, self.relax.model_free.assemble_scaling_matrix, self.relax.model_free.minimise
            if match('read', function_type):
                return self.relax.model_free.read_results
            if match('write', function_type):
                return self.relax.model_free.write_header, self.relax.model_free.write_results
