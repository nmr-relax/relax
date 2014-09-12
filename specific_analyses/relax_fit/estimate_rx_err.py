###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""Estimation of rx error, from Co-variance matrix."""

# Python module imports.
from copy import deepcopy
from numpy import asarray, diag, sqrt, transpose
import sys
from warnings import warn

# relax module imports.
from dep_check import C_module_exp_fn
from lib.errors import RelaxError
from lib.statistics import multifit_covar
from lib.text.sectioning import subsection
from lib.warnings import RelaxWarning
from pipe_control.mol_res_spin import generate_spin_string, spin_loop

# C modules.
if C_module_exp_fn:
    from target_functions.relax_fit import jacobian, jacobian_chi2, setup


def estimate_rx_err(spin_id=None, epsrel=0.0, verbosity=2):
    """This will estimate the rx and i0 errors from the covariance matrix Qxx.  Qxx is calculated from the Jacobian matrix and the optimised parameters.

    @keyword spin_id:       The spin identification string.
    @type spin_id:          str
    @param epsrel:          Any columns of R which satisfy |R_{kk}| <= epsrel |R_{11}| are considered linearly-dependent and are excluded from the covariance matrix, where the corresponding rows and columns of the covariance matrix are set to zero.
    @type epsrel:           float
    @keyword verbosity:     The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:        int
    """

    # Check that the C modules have been compiled.
    if not C_module_exp_fn:
        raise RelaxError("Relaxation curve fitting is not available.  Try compiling the C modules on your platform.")

    # Perform checks.
    if not cdp.curve_type == 'exp':
        raise RelaxError("Only curve type of 'exp' is allowed for error estimation.  Set by: relax_fit.select_model('exp').")

    # Loop over the spins.
    for cur_spin, mol_name, resi, resn, cur_spin_id in spin_loop(selection=spin_id, full_info=True, return_id=True, skip_desel=True):
        # Generate spin string.
        spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

        # Raise Error, if not optimised.
        if not (hasattr(cur_spin, 'rx') and hasattr(cur_spin, 'i0')):
            raise RelaxError("Spin '%s' does not contain optimised 'rx' and 'i0' values.  Try execute: minimise.execute(min_algor='Newton', constraints=False)"%(spin_string))

        # Raise warning, if gradient count is 0.  This could point to a lack of minimisation first.
        if hasattr(cur_spin, 'g_count'):
            if getattr(cur_spin, 'g_count') == 0.0:
                text = "Spin %s contains a gradient count of 0.0.  Is the rx parameter optimised?  Try execute: minimise.execute(min_algor='Newton', constraints=False)" %(spin_string)
                warn(RelaxWarning("%s." % text))

        # Print information.
        if verbosity >= 1:
            # Individual spin block section.
            top = 2
            if verbosity >= 2:
                top += 2
            subsection(file=sys.stdout, text="Estimating rx error for spin: %s"%spin_string, prespace=top)

        # The keys.
        keys = list(cur_spin.peak_intensity.keys())

        # The peak intensities and times.
        values = []
        errors = []
        times = []
        for key in keys:
            values.append(cur_spin.peak_intensity[key])
            errors.append(cur_spin.peak_intensity_err[key])
            times.append(cdp.relax_times[key])

        # Convert to numpy array.
        values = asarray(values)
        errors = asarray(errors)
        times = asarray(times)

        # Extract values.
        rx = getattr(cur_spin, 'rx')
        i0 = getattr(cur_spin, 'i0')

        # Pack data
        param_vector = [rx, i0]

        # Initialise data in C code.
        scaling_list = [1.0, 1.0]
        setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

        # Use the direct Jacobian from function.
        jacobian_matrix_exp = transpose(asarray( jacobian(param_vector) ) )
        weights = 1. / errors**2

        # Get the co-variance
        pcov = multifit_covar(J=jacobian_matrix_exp, weights=weights)

        # To compute one standard deviation errors on the parameters, take the square root of the diagonal covariance.
        param_vector_error = sqrt(diag(pcov))

        # Extract values.
        rx_err, i0_err = param_vector_error

        # Copy rx, to rx_err, if not exists.
        if not hasattr(cur_spin, 'rx_err'):
            setattr(cur_spin, 'rx_err', deepcopy(getattr(cur_spin, 'rx')))
        if not hasattr(cur_spin, 'i0_err'):
            setattr(cur_spin, 'i0_err', deepcopy(getattr(cur_spin, 'i0')))

        # Set error.
        cur_spin.rx_err = rx_err
        cur_spin.i0_err = i0_err

        # Get other relevant information.
        chi2 = getattr(cur_spin, 'chi2')

        # Print information.
        print_strings = []
        if verbosity >= 1:
            # Add print strings.
            point_info = "Spin: '%s', with %i time points." % (spin_string, len(times))
            print_strings.append(point_info)

            par_info = "rx=%3.3f rx_err=%3.4f, i0=%6.1f, i0_err=%3.4f, chi2=%3.3f.\n" % ( rx, rx_err, i0, i0_err, chi2)
            print_strings.append(par_info)

            if verbosity >= 2:
                time_info = ', '.join(map(str, times))
                print_strings.append('For time array: '+time_info+'.\n\n')

        # Print info
        if len(print_strings) > 0:
            for print_string in print_strings:
                print(print_string),
