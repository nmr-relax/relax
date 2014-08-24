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

# Python module imports.
from os import sep
from numpy import asarray, diag, exp, log, sqrt, sum
from scipy.optimize import leastsq
import warnings

# relax module imports.
from pipe_control.mol_res_spin import generate_spin_string, return_spin, spin_loop
#from specific_analyses.relax_disp.data import average_intensity, generate_r20_key, get_curve_type, has_exponential_exp_type, has_r1rho_exp_type, loop_exp_frq, loop_exp_frq_offset_point, loop_exp_frq_offset_point_time, loop_time, return_grace_file_name_ini, return_param_key_from_data
from specific_analyses.relax_disp.data import average_intensity, find_intensity_keys, loop_exp_frq_offset_point, loop_time, return_param_key_from_data
from status import Status; status = Status()
from target_functions.chi2 import chi2_rankN

# Initial try for Exponential class.
from target_functions.relax_disp_curve_fit import Exponential

# Define data path.
prev_data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'Kjaergaard_et_al_2013' +sep+ "check_graphs" +sep+ "mc_2000"  +sep+ "R2eff"

# Create pipe.
pipe.create('MC_2000', 'relax_disp')

# Read results for 2000 MC simulations.
results.read(prev_data_path + sep + 'results')

# Start dic.
my_dic = {}
param_key_list = []

for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    # Add key to dic.
    my_dic[spin_id] = {}
    
    # Generate spin string.
    spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

    print("Optimised parameters for spin: %s" % (spin_string))

    for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
        # Generate the param_key.
        param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

        # Append key.
        param_key_list.append(param_key)

        # Add key to dic.
        my_dic[spin_id][param_key] = {}

        # Get the value.
        r2eff = getattr(cur_spin, 'r2eff')[param_key]
        r2eff_err = getattr(cur_spin, 'r2eff_err')[param_key]
        i0 = getattr(cur_spin, 'i0')[param_key]
        i0_err = getattr(cur_spin, 'i0_err')[param_key]

        # Save to dic.
        my_dic[spin_id][param_key]['r2eff'] = r2eff
        my_dic[spin_id][param_key]['r2eff_err'] = r2eff_err
        my_dic[spin_id][param_key]['i0'] = i0
        my_dic[spin_id][param_key]['i0_err'] = i0_err

        print("r2eff=%3.3f +/- %3.3f , i0=%3.3f +/- %3.3f" % (r2eff, r2eff_err, i0, i0_err) )

# Copy all setup information from base pipe.
pipe.copy(pipe_from='MC_2000', pipe_to='r2eff_est')

for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    # Generate spin string.
    spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

    for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
        # Generate the param_key.
        param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

        ## Now try do a line of best fit by least squares.
        # The peak intensities, errors and times.
        values = []
        errors = []
        times = []
        for time, ti in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point, return_indices=True):
            value = average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, sim_index=None)
            values.append(value)

            error = average_intensity(spin=cur_spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True)
            errors.append(error)
            times.append(time)

            # Find intensity keys.
            int_keys = find_intensity_keys(exp_type=exp_type, frq=frq, offset=offset, point=point, time=time)
            #print type(int_keys)
            # Loop over the replicates.
            #for i in range(len(int_keys)):
                #print( cur_spin.peak_intensity[int_keys[i]], value )
                #print( cur_spin.peak_intensity_err[int_keys[i]], error)

        # Convert to numpy array.
        values = asarray(values)
        errors = asarray(errors)
        times = asarray(times)

        # Estimate the starting parameters, by converting to a linear problem.
        # y= A exp(x * k)
        # w[i] = ln(y[i])
        # int[i] = i0 * exp( - times[i] * r2eff);
        w = log(values)
        x = - 1. * times
        n = len(times)

        b = (sum(x*w) - 1./n * sum(x) * sum(w) ) / ( sum(x**2) - 1./n * (sum(x))**2 )
        a = 1./n * sum(w) - b * 1./n * sum(x)

        # Convert back from linear to exp function. Best estimate for parameter.
        r2eff_est = b
        i0_est = exp(a)

        # Initialise class with different functions.
        exp_class = Exponential()

        # Define initial guess.
        p0 = [r2eff_est, i0_est]

        # 'xtol': Relative error desired in the approximate solution.
        # 'ftol': Relative error desired in the sum of squares.
        #xtol = 1.49012e-08
        xtol = 1e-15
        ftol = xtol

        # 'factor': float, optional. A parameter determining the initial step bound (``factor * || diag * x||``).  Should be in the interval ``(0.1, 100)``.
        factor= 100

        # maxfev : int, optional. The maximum number of calls to the function
        maxfev = 10000000

        # Define function to minimise.
        use_weights = True
        # If 'sigma'/erros describes one standard deviation errors of the input data points. The estimated covariance in 'pcov' is based on these values.
        absolute_sigma = True

        if use_weights:
            func = exp_class.func_exp_weighted_general
            weights = 1.0 / asarray(errors)
            #weights = 1.0 / (2. *asarray(errors) )
            #weights = 1.0 / asarray(errors)**2
            args=(times, values, weights )
        else:
            func = exp_class.func_exp_general
            args=(times, values)

        # Call scipy.optimize.leastsq.
        popt, pcov, infodict, errmsg, ier = leastsq(func=func, x0=p0, args=args, full_output=True, ftol=ftol, xtol=xtol, maxfev=maxfev, factor=factor)

        # Catch errors:
        if ier in [1, 2, 3, 4]:
            warning = None
        elif ier in [4]:
            warnings.warn(errmsg, RuntimeWarning)
            warning = errmsg
        elif ier in [0, 5, 6, 7, 8]:
            raise RuntimeWarning(errmsg)

        # 'nfev' number of function calls.
        f_count = infodict['nfev']

        # 'fvec': function evaluated at the output.
        fvec = infodict['fvec']
        #fvec_test = func(popt, times, values)

        # 'fjac': A permutation of the R matrix of a QR factorization of the final approximate Jacobian matrix, stored column wise. Together with ipvt, the covariance of the estimate can be approximated.
        # fjac = infodict['fjac']

        # 'qtf': The vector (transpose(q) * fvec).
        # qtf = infodict['qtf']

        # 'ipvt'  An integer array of length N which defines a permutation matrix, p, such that fjac*p = q*r, where r is upper triangular
        # with diagonal elements of nonincreasing magnitude. Column j of p is column ipvt(j) of the identity matrix.

        # Back calc fitted curve.
        back_calc = exp_class.calc_exp(times=times, r2eff=popt[0], i0=popt[1])

        # Calculate chi2.
        chi2 = chi2_rankN(data=values, back_calc_vals=back_calc, errors=errors)

        # 'pcov': The estimated covariance of popt.
        # The diagonals provide the variance of the parameter estimate.

        if pcov is None:
            # indeterminate covariance
            pcov = zeros((len(popt), len(popt)), dtype=float)
            pcov.fill(inf)
        elif not absolute_sigma:
            if len(values) > len(p0):
                s_sq = sum( fvec**2 ) / (len(values) - len(p0))
                pcov = pcov * s_sq
            else:
                pcov.fill(inf)

        # To compute one standard deviation errors on the parameters, take the square root of the diagonal covariance.
        perr = sqrt(diag(pcov))

        print_info = True

        if print_info:
            r2eff = popt[0]
            i0 = popt[1]
            r2eff_err = perr[0]
            i0_err = perr[1]
            print("r2eff=%3.3f +/- %3.3f , i0=%3.3f +/- %3.3f" % (r2eff, r2eff_err, i0, i0_err) )

