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


    def setup(self, type, eqi):
        """Setup function."""

        # Model-free analysis.
        if match('mf', eqi):
            if match('fixed', type):
                return self.relax.model_free.create_param_vector, self.relax.model_free.fixed_setup, self.relax.model_free.minimise
            elif match('grid_search', type):
                return self.relax.model_free.create_param_vector, self.relax.model_free.grid_setup, self.relax.model_free.minimise
            elif match('linear_constraints', type):
                return self.relax.model_free.linear_constraints
            elif match('map_labels', type):
                return self.relax.model_free.map_labels
            elif match('map_space', type):
                return self.relax.model_free.create_param_vector, self.relax.model_free.map_bounds, self.relax.model_free.minimise
            elif match('minimise', type):
                return self.relax.model_free.create_param_vector, self.relax.model_free.minimise
            elif match('print', type):
                return self.relax.model_free.print_header, self.relax.model_free.print_results

        # Unknown equation type.
        else:
            print "The equation " + `eqi` + " has not been coded."
            return

