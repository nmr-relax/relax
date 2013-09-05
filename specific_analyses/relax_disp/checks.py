###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Module for functions for checking different aspects of the dispersion setup.

These functions raise various RelaxErrors to help the user understand what went wrong.  To avoid circular imports, these functions must be independent and not import anything from the specific_analyses.relax_disp package (the variables module is an exception).
"""

# relax module imports.
from dep_check import C_module_exp_fn
from lib.errors import RelaxError, RelaxFuncSetupError
import specific_analyses
from specific_analyses.relax_disp.variables import EXP_TYPE_LIST_FIXED_TIME, EXP_TYPE_LIST_VAR_TIME


def check_c_modules():
    """Check for the presence of the compiled C-modules.

    @raises RelaxError: If the compiled C-module is not present and exponential curves are required.
    """

    # Loop over the experiment types.
    for exp_type in cdp.exp_type_list:
        if exp_type in EXP_TYPE_LIST_VAR_TIME and not C_module_exp_fn:
            raise RelaxError("The exponential curve-fitting C module cannot be found.")


def check_disp_points():
    """Check that the CPMG frequencies or spin-lock field strengths have been set up.

    @raises RelaxError: If the dispersion point data is missing.
    """

    # Test if the curve count exists.
    if not hasattr(cdp, 'dispersion_points'):
        raise RelaxError("The CPMG frequencies or spin-lock field strengths have not been set up.")


def check_exp_type():
    """Check if the experiment types have been set up.

    @raises RelaxError: If the dispersion experiment type has not been set.
    """

    # Test if the experiment type is set.
    if not hasattr(cdp, 'exp_type'):
        raise RelaxError("The relaxation dispersion experiment type has not been set for any spectra.")

    # Check each spectrum ID.
    for id in cdp.spectrum_ids:
        if id not in cdp.exp_type:
            raise RelaxError("The relaxation dispersion experiment type has not been set for the %s spectrum." % id)


def check_exp_type_fixed_time():
    """Check that only fixed time experiment types have been set up.

    @raises RelaxError: If exponential curves are present.
    """

    # Loop over all experiment types.
    for exp_type in cdp.exp_type_list:
        if exp_type in EXP_TYPE_LIST_VAR_TIME:
            raise RelaxError("The experiment '%s' is not of the fixed relaxation time period data type." % exp_type)


def check_mixed_curve_types():
    """Prevent both fixed time and exponential curves from being analysed simultaneously.

    @raises RelaxError: If mixed curve types are present.
    """

    # Loop over all experiment types.
    var_flag = False
    fixed_flag = False
    for exp_type in cdp.exp_type_list:
        if exp_type in EXP_TYPE_LIST_VAR_TIME:
            var_flag = True
        if exp_type in EXP_TYPE_LIST_FIXED_TIME:
            fixed_flag = True

    # The check.
    if var_flag and fixed_flag:
        raise RelaxError("Fixed time and exponential curves cannot be analysed simultaneously.")


def check_model_type():
    """Check that the dispersion model has been set.

    @raises RelaxError: If the dispersion model has not been specified.
    """

    # Test if the model has been set.
    if not hasattr(cdp, 'model_type'):
        raise RelaxError("The relaxation dispersion model has not been specified.")


def check_pipe_type():
    """Check that the data pipe type is that of relaxation dispersion.

    @raises RelaxFuncSetupError:    If the data pipe type is not set to 'relax_disp'.
    """

    # Test if the pipe type is set to 'relax_disp'.
    function_type = cdp.pipe_type
    if function_type != 'relax_disp':
        raise RelaxFuncSetupError(specific_analyses.setup.get_string(function_type))
