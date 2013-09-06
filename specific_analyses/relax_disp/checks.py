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
from lib.errors import RelaxError, RelaxFuncSetupError, RelaxNoFrqError, RelaxNoPeakIntensityError
import specific_analyses
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG, EXP_TYPE_R1RHO


def check_c_modules():
    """Check for the presence of the compiled C-modules.

    @raises RelaxError: If the compiled C-module is not present and exponential curves are required.
    """

    # Get the times.
    times = get_times()

    # Complain.
    for exp_type in times:
        if len(times[exp_type]) > 1 and not C_module_exp_fn:
            raise RelaxError("The exponential curve-fitting C module cannot be found.")


def check_disp_points():
    """Check that the CPMG frequencies or spin-lock field strengths have been set up.

    @raises RelaxError: If the dispersion point data is missing.
    """

    # Test if the curve count exists.
    if not hasattr(cdp, 'dispersion_points'):
        raise RelaxError("The CPMG frequencies or spin-lock field strengths have not been set for any spectra.")

    # Check each spectrum ID.
    for id in cdp.spectrum_ids:
        # CPMG data.
        if cdp.exp_type[id] == EXP_TYPE_CPMG:
            if id not in cdp.cpmg_frqs:
                raise RelaxError("The nu_CPMG frequency has not been set for the '%s' spectrum." % id)

        # R1rho data.
        elif cdp.exp_type[id] == EXP_TYPE_R1RHO:
            if id not in cdp.spin_lock_nu1:
                raise RelaxError("The spin-lock field strength has not been set for the '%s' spectrum." % id)


def check_exp_type():
    """Check if the experiment types have been set up.

    @raises RelaxError: If the dispersion experiment type has not been set.
    """

    # Test if the experiment type is set.
    if not hasattr(cdp, 'exp_type'):
        raise RelaxError("The relaxation dispersion experiment types have not been set for any spectra.")

    # Check each spectrum ID.
    for id in cdp.spectrum_ids:
        if id not in cdp.exp_type:
            raise RelaxError("The relaxation dispersion experiment type has not been set for the '%s' spectrum." % id)


def check_exp_type_fixed_time():
    """Check that only fixed time experiment types have been set up.

    @raises RelaxError: If exponential curves are present.
    """

    # Get the times.
    times = get_times()

    # Loop over all experiment types.
    for exp_type in times:
        if len(times[exp_type]) > 1:
            raise RelaxError("The experiment '%s' is not of the fixed relaxation time period data type." % exp_type)


def check_mixed_curve_types():
    """Prevent both fixed time and exponential curves from being analysed simultaneously.

    @raises RelaxError: If mixed curve types are present.
    """

    # No experiment types set.
    if not hasattr(cdp, 'exp_type') or not hasattr(cdp, 'spectrum_ids') or not hasattr(cdp, 'relax_times'):
        return False

    # Get the times.
    times = get_times()

    # Loop over all experiment types.
    var_flag = False
    fixed_flag = False
    for exp_type in times:
        if times[exp_type] == 1:
            fixed_flag = True
        else:
            var_flag = True

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


def check_relax_times():
    """Check if the spectrometer frequencies have been set up.

    @raises RelaxError: If the spectrometer frequencies have not been set.
    """

    # Test if the experiment type is set.
    if not hasattr(cdp, 'relax_times'):
        raise RelaxError("The relaxation times have not been set for any spectra.")

    # Check each spectrum ID.
    for id in cdp.spectrum_ids:
        if id not in cdp.relax_times:
            raise RelaxError("The relaxation time has not been set for the '%s' spectrum." % id)


def check_spectra_id_setup():
    """Check that the data for each spectra ID is correctly set up.

    This is an alias for the following checks:

        - check_spectrum_ids()
        - check_exp_type()
        - check_spectrometer_frq()
        - check_disp_points()
        - check_relax_times()


    @raises RelaxError: If data is missing.
    """

    # Perform the checks.
    check_spectrum_ids()
    check_exp_type()
    check_spectrometer_frq()
    check_disp_points()
    check_relax_times()


def check_spectrometer_frq():
    """Check if the spectrometer frequencies have been set up.

    @raises RelaxError: If the spectrometer frequencies have not been set.
    """

    # Test if the experiment type is set.
    if not hasattr(cdp, 'spectrometer_frq'):
        raise RelaxError("The spectrometer frequencies have not been set for any spectra.")

    # Check each spectrum ID.
    for id in cdp.spectrum_ids:
        if id not in cdp.spectrometer_frq:
            raise RelaxError("The spectrometer frequency has not been set for the '%s' spectrum." % id)


def check_spectrum_ids():
    """Check if spectrum IDs exist.

    @raises RelaxNoPeakIntensityError:  If no spectrum IDs exist.
    """

    # The spectrum IDs structure.
    if not hasattr(cdp, 'spectrum_ids') or len(cdp.spectrum_ids) == 0:
        raise RelaxNoPeakIntensityError


def get_times():
    """Create a per-experiment dictionary of relaxation times.
    
    @return:    The dictionary of unique relaxation times.
    @rtype:     dict of float
    """

    # Initialise.
    times = {}
    for type in cdp.exp_type_list:
        times[type] = []

    # No experiment types set.
    if not hasattr(cdp, 'exp_type') or not hasattr(cdp, 'spectrum_ids') or not hasattr(cdp, 'relax_times'):
        return times

    # Loop over all spectra IDs.
    for id in cdp.spectrum_ids:
        # Count the number of times.
        if cdp.relax_times[id] not in times[cdp.exp_type[id]]:
            times[cdp.exp_type[id]].append(cdp.relax_times[id])

    # Return the times dictionary.
    return times
