###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the minfx optimisation library,                        #
# https://gna.org/projects/minfx                                              #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Package docstring.
"""This is the U{minfx optimisation library<https://gna.org/projects/minfx>}."""

# The minfx version.
__version__ = '1.0.12'

# List of all modules.
__all__ = [ 'base_classes',
            'bfgs',
            'cauchy_point',
            'constraint_linear',
            'coordinate_descent',
            'dogleg',
            'exact_trust_region',
            'fletcher_reeves_cg',
            'generic',
            'grid',
            'hestenes_stiefel_cg',
            'levenberg_marquardt',
            'log_barrier_function',
            'method_of_multipliers',
            'ncg',
            'newton',
            'polak_ribiere_cg',
            'polak_ribiere_plus_cg',
            'simplex',
            'steepest_descent',
            'steihaug_cg' ]
