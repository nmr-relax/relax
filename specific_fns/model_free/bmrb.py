###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# relax module imports.
from bmrblib.nmr_star_dict import NMR_STAR
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import get_pipe


class Bmrb:
    """Class containing methods related to BMRB STAR file reading and writing."""

    def bmrb_read(self, file_path):
        """Read the model-free results from a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the NMR-STAR data object.
        star = NMR_STAR('relax_model_free_results', file_path)

        # Read the contents of the STAR formatted file.
        star.read()


    def bmrb_write(self, file_path):
        """Write the model-free results to a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the NMR-STAR data object.
        star = NMR_STAR('relax_model_free_results', file_path)

        # Get the current data pipe.
        cdp = get_pipe()

        # Initialise the spin specific data lists.
        res_num_list = []
        res_name_list = []
        atom_name_list = []
        relax_data_list = []
        relax_error_list = []
        for i in range(cdp.num_ri):
            relax_data_list.append([])
            relax_error_list.append([])

        # Store the spin specific data in lists for later use.
        for spin, mol_name, res_num, res_name in spin_loop(full_info=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # The residue/spin info.
            res_num_list.append(str(res_num))
            res_name_list.append(str(res_name))
            atom_name_list.append(str(spin.name))

            # The relaxation data.
            for i in range(cdp.num_ri):
                relax_data_list[i].append(str(spin.relax_data[i]))
                relax_error_list[i].append(str(spin.relax_error[i]))

        # Add the relaxation data.
        for i in range(cdp.num_ri):
            star.heteronucl_T1_relaxation.add(ri_label=cdp.ri_labels[i], frq=cdp.frq[cdp.remap_table[i]], res_nums=res_num_list, res_names=res_name_list, atom_names=atom_name_list, data=relax_data_list[i], errors=relax_error_list[i])

        # Write the contents to the STAR formatted file.
        star.write()
