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
from generic_fns.mol_res_spin import spin_loop
from generic_fns.pipes import get_pipe
from pystarlib.File import File
from pystarlib.SaveFrame import SaveFrame
from pystarlib.TagTable import TagTable


class Bmrb:
    """Class containing methods related to BMRB STAR file reading and writing."""

    def bmrb_read(self, file_path):
        """Read the model-free results from a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the pystarlib File object.
        file = File(title='relax_model_free_results', filename=file_path)

        # Read the contents of the STAR formatted file.
        file.read()


    def bmrb_write(self, file_path):
        """Write the model-free results to a BMRB NMR-STAR v3.1 formatted file.

        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the pystarlib File object.
        file = File(title='relax_model_free_results', filename=file_path)

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

        # Relaxation data save frames.
        r1_inc = 0
        r2_inc = 0
        noe_inc = 0
        for i in range(cdp.num_ri):
            # Data type labels.
            if cdp.ri_labels[i] == 'R1':
                r1_inc = r1_inc + 1
                ri_inc = r1_inc
                ri_label = 'T1'
                coherence = 'Nz'
            elif cdp.ri_labels[i] == 'R2':
                r2_inc = r2_inc + 1
                ri_inc = r2_inc
                ri_label = 'T2'
                coherence = 'Ny'
            elif cdp.ri_labels[i] == 'NOE':
                noe_inc = noe_inc + 1
                ri_inc = noe_inc
                ri_label = 'NOE'

            # Initialise the save frame.
            frame = SaveFrame(title='heteronuclear_'+ri_label+'_list_'+`ri_inc`)

            # The save frame category.
            frame.tagtables.append(TagTable(free=True, tagnames=['_Saveframe_category'], tagvalues=[[ri_label+'_relaxation']]))

            # Sample info.
            frame.tagtables.append(TagTable(free=True, tagnames=['_Sample_label'], tagvalues=[['$sample_1']]))
            frame.tagtables.append(TagTable(free=True, tagnames=['_Sample_conditions_label'], tagvalues=[['$conditions_1']]))

            # NMR info.
            frame.tagtables.append(TagTable(free=True, tagnames=['_Spectrometer_frequency_1H'], tagvalues=[[str(cdp.frq[cdp.remap_table[i]]/1e6)]]))
            if ri_label in ['T1', 'T2']:
                frame.tagtables.append(TagTable(free=True, tagnames=['_'+ri_label+'_coherence_type'], tagvalues=[[coherence]]))
                frame.tagtables.append(TagTable(free=True, tagnames=['_'+ri_label+'_value_units'], tagvalues=[['1/s']]))

            # The relaxation tag names.
            tag_names = ['_Residue_seq_code', '_Residue_label', '_Atom_name', '_'+ri_label+'_value', '_'+ri_label+'_value_error']

            # Add the data.
            table = TagTable(tagnames=tag_names, tagvalues=[res_num_list, res_name_list, atom_name_list, relax_data_list[i], relax_error_list[i]])

            # Add the tag table to the save frame.
            frame.tagtables.append(table)

            # Add the relaxation data save frame.
            file.datanodes.append(frame)

        # Write the contents to the STAR formatted file.
        file.write()
