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

# Python module imports.
from numpy import average

# relax module imports.
from lib.mathematics import round_to_next_order
from specific_analyses.parameter_object import Param_list


def i_scaling(model_info=None):
    """Determine the scaling factor for the peak intensities.

    This is for the scaling of the I0 and Iinf parameters during optimisation.  The maximum intensity will be used to scale all values.


    @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() specific API method.
    @type model_info:       SpinContainer instance, str
    @return:                The average peak intensity of the first time point.
    @rtype:                 float
    """

    # Unpack the data.
    spin, spin_id = model_info

    # The scaling factor as the maximum intensity.
    return round_to_next_order(max(spin.peak_intensity.values()))


def i0_upper(incs=None, model_info=None):
    """Find the upper bound for the I0 parameter.

    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() specific API method.
    @type model_info:       SpinContainer instance, str
    @return:                The average peak intensity of the first time point.
    @rtype:                 float
    """

    # Unpack the data.
    spin, spin_id = model_info

    # Find the maximum intensity.
    upper = max(spin.peak_intensity.values())

    # Multiply the value by 2.0 and then round up to the next order - this will be the upper bound.
    return round_to_next_order(upper * 2.0)


def iinf_upper(incs=None, model_info=None):
    """Find the average intensity of the last time point.

    This is for the grid search upper bound for the Iinf parameter.


    @keyword incs:          The number of grid search increments.
    @type incs:             int
    @keyword model_info:    The spin container and the spin ID string from the _model_loop_spin() specific API method.
    @type model_info:       SpinContainer instance, str
    @return:                The average peak intensity of the last time point.
    @rtype:                 float
    """

    # Unpack the data.
    spin, spin_id = model_info

    # Find the ID of the last time point.
    max_time = max(cdp.relax_times.values())
    for key in cdp.relax_times:
        if cdp.relax_times[key] == max_time:
            id = key
            break

    # The averaged value.
    upper = average(spin.peak_intensity[id])

    # Multiply the value by 2.0 and then round up to the next order - this will be the upper bound.
    return round_to_next_order(upper * 2.0)



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

        # Add the signal to noise ratio.
        self._add_sn_ratio()

        # Add the base information for the analysis.
        self._add(
            'relax_times',
            scope = 'spin',
            py_type = dict,
            grace_string = '\\qRelaxation time period (s)\\Q'
        )

        # Add the model variables.
        self._add_model_info(model_flag=False)

        # Add the model parameters.
        self._add(
            'rx',
            scope = 'spin',
            default = 8.0,
            units = 'rad.s^-1',
            desc = 'Either the R1 or R2 relaxation rate',
            set = 'params',
            py_type = float,
            scaling = 1.0,
            grid_lower = 0.0,
            grid_upper = 20.0,
            grace_string = '\\qR\\sx\\Q',
            err = True,
            sim = True
        )
        self._add(
            'i0',
            scope = 'spin',
            default = 10000.0,
            desc = 'The initial intensity',
            py_type = float,
            set = 'params',
            scaling = i_scaling,
            grid_lower = 0.0,
            grid_upper = i0_upper,
            grace_string = '\\qI\\s0\\Q',
            err = True,
            sim = True
        )
        self._add(
            'iinf',
            scope = 'spin',
            default = 0.0,
            desc = 'The intensity at infinity',
            py_type = float,
            set = 'params',
            scaling = i_scaling,
            grid_lower = 0.0,
            grid_upper = iinf_upper,
            grace_string = '\\qI\\sinf\\Q',
            err = True,
            sim = True
        )

        # Add the minimisation data.
        self._add_min_data(min_stats_global=False, min_stats_spin=True)

        # Set up the user function documentation.
        self._set_uf_title("Relaxation curve fitting parameters")
        self._uf_param_table(label="table: curve-fit parameters", caption="Relaxation curve fitting parameters.")
        self._uf_param_table(label="table: curve-fit parameters and min stats", caption="Relaxation curve fitting parameters and minimisation statistics.", sets=['params', 'fixed', 'min'])
        self._uf_param_table(label="table: curve-fit parameter value setting", caption="Relaxation curve fitting parameters.")
        self._uf_param_table(label="table: curve-fit parameter value setting with defaults", caption="Relaxation curve fitting parameter value setting.", default=True)
