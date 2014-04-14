###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
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
"""The module for the relaxation curve fitting parameter list object."""

# relax module imports.
from specific_analyses.parameter_object import Param_list


class Relax_fit_params(Param_list):
    """The relaxation curve fitting parameter list singleton."""

    # Class variable for storing the class instance (for the singleton design pattern).
    _instance = None

    def __init__(self):
        """Define all the parameters of the analysis."""

        # The object is already initialised.
        if self._initialised: return

        # Execute the base class __init__() method.
        Param_list.__init__(self)

        # Add the base data.
        self._add_peak_intensity()

        # Add the base information for the analysis.
        self._add('relax_times', scope='spin', py_type=dict, grace_string='\\qRelaxation time period (s)\\Q')

        # Add the model variables.
        self._add_model_info(model_flag=False)

        # Add the model parameters.
        self._add('rx', scope='spin', default=8.0, desc='Either the R1 or R2 relaxation rate', set='params', py_type=float, grace_string='\\qR\\sx\\Q', err=True, sim=True)
        self._add('i0', scope='spin', default=10000.0, desc='The initial intensity', py_type=float, set='params', grace_string='\\qI\\s0\\Q', err=True, sim=True)
        self._add('iinf', scope='spin', default=0.0, desc='The intensity at infinity', py_type=float, set='params', grace_string='\\qI\\sinf\\Q', err=True, sim=True)

        # Add the minimisation data.
        self._add_min_data(min_stats_global=False, min_stats_spin=True)

        # Set up the user function documentation.
        self._set_uf_title("Relaxation curve fitting parameters")
        self._uf_param_table(label="table: curve-fit parameters", caption="Relaxation curve fitting parameters.")
        self._uf_param_table(label="table: curve-fit parameters and min stats", caption="Relaxation curve fitting parameters and minimisation statistics.", sets=['params', 'fixed', 'min'])
        self._uf_param_table(label="table: curve-fit parameter value setting", caption="Relaxation curve fitting parameters.")
        self._uf_param_table(label="table: curve-fit parameter value setting with defaults", caption="Relaxation curve fitting parameter value setting.", default=True)
