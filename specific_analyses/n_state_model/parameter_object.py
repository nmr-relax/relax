###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
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

# Module docstring.
"""The module for the N-state model parameter list object."""

# Python module imports.
from math import pi

# relax module imports.
from specific_analyses.parameter_object import Param_list


class N_state_params(Param_list):
    """The N-state model parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # The object is already initialised.
        if self._initialised: return

        # Execute the base class __init__() method.
        Param_list.__init__(self)

        # Add the base data.
        self._add_align_data()
        self._add_align_tensor()

        # Add up the model parameters.
        self._add(
            'probs',
            scope = 'global',
            default = 0.0,
            desc = 'The probabilities of each state',
            py_type = list,
            set = 'params',
            scaling = 0.1,
            grid_lower = 0.0,
            grid_upper = 1.0,
            err = True,
            sim = True
        )
        self._add(
            'alpha',
            scope = 'global',
            units = 'rad',
            default = 0.0,
            desc = 'The alpha Euler angles (for the rotation of each state)',
            py_type = list,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 2*pi,
            err = True,
            sim = True
        )
        self._add(
            'beta',
            scope = 'global',
            units = 'rad',
            default = 0.0,
            desc = 'The beta Euler angles (for the rotation of each state)',
            py_type = list,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 2*pi,
            err = True,
            sim = True
        )
        self._add(
            'gamma',
            scope = 'global',
            units = 'rad',
            default = 0.0,
            desc = 'The gamma Euler angles (for the rotation of each state)',
            py_type = list,
            set = 'params',
            grid_lower = 0.0,
            grid_upper = 2*pi,
            err = True,
            sim = True
        )
        self._add(
            'paramagnetic_centre',
            scope = 'global',
            units = 'Angstrom',
            desc = 'The paramagnetic centre',
            py_type = list,
            set = 'params',
            scaling = 1e2,
            grid_lower = -100.0,
            grid_upper = 100,
            err = True,
            sim = True
        )

        # Add the minimisation data.
        self._add_min_data(min_stats_global=False, min_stats_spin=True)

        # Set up the user function documentation.
        self._set_uf_title("N-state model parameters")
        self._uf_param_table(label="table: N-state parameters", caption="N-state model parameters.", scope='global', type=True)
        self._uf_param_table(label="table: N-state parameter value setting", caption="N-state model parameters.", scope='global', type=True)
        self._uf_param_table(label="table: N-state parameter value setting with defaults", caption="N-state model parameter value setting.", scope='global', default=True, type=True)

        # Value setting documentation.
        for doc in self._uf_doc_loop(["table: N-state parameter value setting", "table: N-state parameter value setting with defaults"]):
            doc.add_paragraph("Setting parameters for the N-state model is a little different from the other type of analyses as each state has a set of parameters with the same names as the other states.  To set the parameters for a specific state c (ranging from 0 for the first to N-1 for the last, the number c should be given as the index argument.  So the Euler angle gamma of the third state is specified using the parameter name 'gamma' and index of 2.")
