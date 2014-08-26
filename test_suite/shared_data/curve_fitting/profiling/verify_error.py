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
from specific_analyses.relax_disp.estimate_r2eff import minimise_leastsq, Exp

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

# Instantiate class.
E = Exp(verbosity=1)

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

        # Initialise the function to minimise.
        E.setup_data(values=values, errors=errors, times=times)

        # Initial guess for minimisation. Solved by linear least squares.
        x0 = asarray( E.estimate_x0_exp() )

        results = minimise_leastsq(E=E)

        # Unpack results
        param_vector, param_vector_error, chi2, iter_count, f_count, g_count, h_count, warning = results

        if E.verbosity:
            r2eff = param_vector[0]
            i0 = param_vector[1]
            r2eff_err = param_vector_error[0]
            i0_err = param_vector_error[1]
            print("r2eff=%3.3f +/- %3.3f , i0=%3.3f +/- %3.3f" % (r2eff, r2eff_err, i0, i0_err) )

