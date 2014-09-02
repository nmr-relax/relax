###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Troels E. Linnet                                    #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
# Script for calculating synthetics CPMG data.

# Python module imports.
from math import sqrt
from collections import OrderedDict
import cPickle as pickle
from os import getcwd, makedirs, path, sep
from numpy import array, asarray, diag, ones, std, sqrt

# relax module imports.
from lib.io import open_write_file
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import generate_spin_string, return_spin, spin_loop
from specific_analyses.relax_disp.data import generate_r20_key, loop_exp_frq, loop_offset_point, loop_exp_frq_offset_point, return_param_key_from_data
from specific_analyses.relax_disp import optimisation
from status import Status; status = Status()

# After Monte-Carlo.
data_path = status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'estimate_par_err'+sep+'cr72'
resultsfile_mc = 'final_results_mc'
pipe.create(pipe_name='mc pipe', pipe_type='relax_disp')
results.read(file=resultsfile_mc, dir=data_path)

sim_attr_list = ['chi2_sim', 'f_count_sim', 'g_count_sim', 'h_count_sim', 'iter_sim', 'peak_intensity_sim', 'select_sim', 'warning_sim']
sim_attr_list = sim_attr_list + ['r2eff_sim', 'r2_sim', 'pA_sim', 'pB_sim', 'dw_sim', 'kex_sim','k_AB_sim', 'k_BA_sim', 'tex_sim']

# Start dic.
my_dic = OrderedDict()

# Get the data.
for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    # Add key to dic.
    my_dic[spin_id] = OrderedDict()

    # Generate spin string.
    spin_string = generate_spin_string(spin=cur_spin, mol_name=mol_name, res_num=resi, res_name=resn)

    #for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
    for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):

        # Generate the param_key.
        #param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)
        param_key = generate_r20_key(exp_type=exp_type, frq=frq)

        # Add key to dic.
        my_dic[spin_id][param_key] = OrderedDict()

        # Loop over all sim, and collect data.
        #r2eff_sim_l = [] 
        r2_sim_l = []
        pA_sim_l = []
        dw_sim_l = []
        kex_sim_l = []

        for i, r2eff_sim in enumerate(cur_spin.r2eff_sim):
            r2_sim = cur_spin.r2_sim[i]
            pA_sim = cur_spin.pA_sim[i]
            dw_sim = cur_spin.dw_sim[i]
            kex_sim = cur_spin.kex_sim[i]

            #r2eff_sim_i = r2eff_sim
            #r2eff_sim_l.append(r2eff_sim_i)

            r2_sim_i = r2_sim[param_key]
            r2_sim_l.append(r2_sim_i)

            pA_sim_i = pA_sim
            pA_sim_l.append(pA_sim_i)

            dw_sim_i = dw_sim
            dw_sim_l.append(dw_sim_i)

            kex_sim_i = kex_sim
            kex_sim_l.append(kex_sim_i)

        #my_dic[spin_id][param_key]['r2eff_array_sim'] = asarray(r2eff_sim_l)
        my_dic[spin_id][param_key]['r2_array_sim'] = asarray(r2_sim_l)
        my_dic[spin_id][param_key]['pA_array_sim'] = asarray(pA_sim_l)
        my_dic[spin_id][param_key]['dw_array_sim'] = asarray(dw_sim_l)
        my_dic[spin_id][param_key]['kex_array_sim'] = asarray(kex_sim_l)

        # Take the standard deviation of all values.
        #r2eff_sim_err = std(asarray(r2eff_sim_l), ddof=1)
        r2_sim_err = std(asarray(r2_sim_l), ddof=1)
        pA_sim_err = std(asarray(pA_sim_l), ddof=1)
        dw_sim_err = std(asarray(dw_sim_l), ddof=1)
        kex_sim_err = std(asarray(dw_sim_l), ddof=1)
        #my_dic[spin_id][param_key]['r2eff_err_sim'] = r2eff_sim_err
        my_dic[spin_id][param_key]['r2_err_sim'] = r2_sim_err
        my_dic[spin_id][param_key]['pA_err_sim'] = pA_sim_err
        my_dic[spin_id][param_key]['dw_err_sim'] = dw_sim_err
        my_dic[spin_id][param_key]['kex_err_sim'] = kex_sim_err

        # Check for correct size.
        if len(r2_sim_l) != 10000:
            print asd


## Loop over spin attributes, to delete them.
for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    for spin_attr in sim_attr_list:
        if hasattr(cur_spin, spin_attr):
            delattr(cur_spin, spin_attr)
            print spin_attr

    print cur_spin

# Write to pickle.
pickle.dump( my_dic, open( "final_results_mc_strip.cp", "wb" ) )

results.write(file='final_results_mc_strip', dir=data_path, force=True)