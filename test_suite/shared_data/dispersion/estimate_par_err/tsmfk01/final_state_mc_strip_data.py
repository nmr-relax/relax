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

# relax module imports.
from lib.io import open_write_file
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.mol_res_spin import return_spin, spin_loop
from specific_analyses.relax_disp.data import generate_r20_key, loop_exp_frq, loop_offset_point
from specific_analyses.relax_disp import optimisation
from status import Status; status = Status()

number = 50000

state.load('final_state_mc%i'%number)

sim_attr_list = ['chi2_sim', 'f_count_sim', 'g_count_sim', 'h_count_sim', 'i0_sim', 'iter_sim', 'peak_intensity_sim', 'r2eff_sim', 'select_sim', 'warning_sim']


# Delete old simulations.
for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
    # Loop over old err attributes.
    for err_attr in err_attr_list:
        if hasattr(cur_spin, err_attr):
            delattr(cur_spin, err_attr)
