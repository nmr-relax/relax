###############################################################################
#                                                                             #
# Copyright (C) 2015 Troels E. Linnet                                         #
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
from pipe_control.mol_res_spin import spin_loop


# Read data
pipe.create(pipe_name='ref_data', pipe_type='relax_disp')
results.read("FT_-_TSMFK01_-_min_mc_-_128_-_free_spins")

pipe.create(pipe_name='new_data', pipe_type='relax_disp')
pipe.switch(pipe_name='new_data')
results.read("coMDD_-_TSMFK01_-_min_mc_-_128_-_free_spins")

pipe.current()
pipe.display()

# Delete data to save disk space
for i_pipe in ['ref_data', 'new_data']:
    pipe.switch(pipe_name=i_pipe)

    # Delete all other than first then 10 spins, to save space
    i = 0
    i_max = 100
    for cur_spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
        print("\n", resi, resn)
        for class_attr in cur_spin.__dict__.keys():
            if class_attr in ["iter_sim", "f_count_sim", "g_count_sim", "h_count_sim", "warning_sim", "r2eff_sim"]:
                # Delete
                delattr(cur_spin, class_attr)
                continue

            if "_sim" in class_attr:
                print(class_attr)

        # Delete spin
        if i > i_max:
            spin.delete(spin_id=spin_id)
            #residue.delete(res_id=spin_id)
            deselect.spin(spin_id=spin_id)

        # Add to counter
        i += 1

state.save("data_state", force=True)
