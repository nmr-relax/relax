###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

"""Script for returning off-resonance R1rho-type data."""


# relax module imports.
from pipe_control.mol_res_spin import find_index, get_spin_ids, return_spin, spin_loop
from specific_analyses.relax_disp.data import loop_exp_frq_offset, return_offset_data, return_param_key_from_data, return_spin_lock_nu1

def generate_theta_dic():
    # Get the field count
    field_count = cdp.spectrometer_frq_count

    # Get the spin_lock_field points
    spin_lock_nu1 = return_spin_lock_nu1(ref_flag=False)

    # Initialize data containers
    all_spin_ids = get_spin_ids()

    # Containers for only selected spins
    cur_spin_ids = []
    cur_spins = []
    for curspin_id in all_spin_ids:
        # Get the spin
        curspin = return_spin(curspin_id)

        # Check if is selected
        if curspin.select == True:
            cur_spin_ids.append(curspin_id)
            cur_spins.append(curspin)

    # The offset and R1 data.
    chemical_shifts, offsets, tilt_angles, Delta_omega, w_eff = return_offset_data(spins=cur_spins, spin_ids=cur_spin_ids, field_count=field_count, fields=spin_lock_nu1)
        
    # Loop over the index of spins, then exp_type, frq, offset
    print("Printing the following")    
    print("exp_type curspin_id frq offset{ppm} offsets[ei][si][mi][oi]{rad/s} ei mi oi si di cur_spin.chemical_shift{ppm} chemical_shifts[ei][si][mi]{rad/s} spin_lock_nu1{Hz} tilt_angles[ei][si][mi][oi]{rad}")
    for si in range(len(cur_spin_ids)):
        theta_spin_dic = dict()
        curspin_id = cur_spin_ids[si]
        cur_spin = cur_spins[si]
        for exp_type, frq, offset, ei, mi, oi in loop_exp_frq_offset(return_indices=True):
            # Loop over the dispersion points.
            spin_lock_fields = spin_lock_nu1[ei][mi][oi]
            for di in range(len(spin_lock_fields)):
                print("%-8s %-10s %11.1f %8.4f %12.5f %i  %i  %i  %i  %i %7.3f %12.5f %12.5f %12.5f"%(exp_type, curspin_id, frq, offset, offsets[ei][si][mi][oi], ei, mi, oi, si, di, cur_spin.chemical_shift, chemical_shifts[ei][si][mi], spin_lock_fields[di], tilt_angles[ei][si][mi][oi][di]))
                dic_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=spin_lock_fields[di])
                theta_spin_dic["%s"%(dic_key)] = tilt_angles[ei][si][mi][oi][di]
        # Store the data
        cur_spin.theta = theta_spin_dic
    
    print("\nThe theta data now resides in")
    for curspin, mol_name, res_num, res_name, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
        spin_index = find_index(selection=spin_id, global_index=False)
        print("%s cdp.mol[%i].res[%i].spin[%i].theta"%(spin_id, spin_index[0], spin_index[1], spin_index[2]))
