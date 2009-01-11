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

        # Store the spin specific data in lists for later use.
        for spin in spin_loop():
            pass

        # Relaxation data save frames.
        for i in range(cdp.num_ri):
            # Data type labels.
            if cdp.ri_labels[i] == 'R1':
                ri_label = 'T1'
                coherence = 'Nz'
            elif cdp.ri_labels[i] == 'R2':
                ri_label = 'T2'
                coherence = 'Ny'
            elif cdp.ri_labels[i] == 'NOE':
                ri_label = 'NOE'
                coherence = 'Ny'

            # Initialise the save frame.
            frame = SaveFrame(title=cdp.ri_labels[i], text='hello')

            # Specifics of the collected data.
            frame.tagtables.append(TagTable(tagnames=['_Sample_conditions_label'], tagvalues=[['$condition_one']]))
            frame.tagtables.append(TagTable(tagnames=['_Spectrometer_frequency_1H'], tagvalues=[[str(cdp.frq[cdp.remap_table[i]]/1e6)]]))
            if ri_label in ['T1', 'T2']:
                frame.tagtables.append(TagTable(tagnames=['_'+ri_label+'_coherence_type'], tagvalues=[[coherence]]))
                frame.tagtables.append(TagTable(tagnames=['_'+ri_label+'_value_units'], tagvalues=[['1/s']]))

            # The relaxation tag names.
            tag_names = ['_Residue_seq_code', '_Residue_label', '_Atom_name', '_'+ri_label+'_value', '_'+ri_label+'_value_error']

            table = TagTable(title='hello', tagnames=tag_names, tagvalues=[['0', '1', '2', '3', '4']])

            # Add the tag table to the save frame.
            frame.tagtables.append(table)

            # Add the relaxation data save frame.
            file.datanodes.append(frame)

        # Write the contents to the STAR formatted file.
        file.write()
