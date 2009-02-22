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

# Module docstring.
"""The base classes for the NMR-STAR dictionary support within relax.

The most up to date NMR-STAR dictionary relax uses is the v3.1 version documented at
http://www.bmrb.wisc.edu/dictionary/3.1html/SuperGroupPage.html.
"""

# relax module imports.
from pystarlib.File import File
from pystarlib.SaveFrame import SaveFrame
from pystarlib.TagTable import TagTable


class NMR_STAR:
    """The base object for the NMR-STAR dictionary."""

    def __init__(self, title, file_path):
        """Initialise the NMR-STAR dictionary object.

        @param title:       The title of the NMR-STAR data.
        @type title:        str
        @param file_path:   The full file path.
        @type file_path:    str
        """

        # Initialise the pystarlib File object.
        self.data = File(title=title, filename=file_path)

        # Initialise the objects of this class.
        self.relax_data = Relaxation_data(self.data.datanodes)


    def read(self):
        """Read the data from a BMRB NMR-STAR formatted file."""

        # Read the contents of the STAR formatted file.
        self.data.read()


    def write(self):
        """Write the data to a BMRB NMR-STAR formatted file."""

        # Write the contents to the STAR formatted file.
        self.data.write()


class Relaxation_data:
    """Base class for relaxation data support."""

    # Tag categories.
    HeteronuclNOEList = None
    HeteronuclT1List = None
    HeteronuclT2List = None

    # Tag names for the relaxation data.
    SfCategory = '_Saveframe_category'
    SampleConditionListLabel = '_Sample_conditions_label'
    SpectrometerFrequency1H = '_Spectrometer_frequency_1H'
    T1CoherenceType = '_T1_coherence_type'
    T2CoherenceType = '_T2_coherence_type'
    T1ValUnits = '_T1_value_units'
    T2ValUnits = '_T2_value_units'

    # Tag names for experiment setup.
    SampleLabel = '_Sample_label'


    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of relaxation data sets.
        self.r1_inc = 0
        self.r2_inc = 0
        self.noe_inc = 0


    def add(self, ri_label=None, frq=None, res_nums=None, res_names=None, atom_names=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword ri_label:      The relaxation data label, one of 'R1', 'R2', or 'NOE'.
        @type ri_label:         str
        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Init.
        tag_cat = ''

        # Set up the R1 specific variables.
        if ri_label == 'R1':
            # Misc.
            self.r1_inc = self.r1_inc + 1
            ri_inc = self.r1_inc
            label = 'T1'
            coherence = 'Nz'

            # Tag categories.
            if self.HeteronuclT1List:
                tag_cat = self.HeteronuclT1List + '.'
            else:
                tag_cat = ''

        # Set up the R2 specific variables.
        elif ri_label == 'R2':
            # Misc.
            self.r2_inc = self.r2_inc + 1
            ri_inc = self.r2_inc
            label = 'T2'
            coherence = 'Ny'

            # Tag categories.
            if self.HeteronuclT2List:
                tag_cat = self.HeteronuclT2List + '.'

        # Set up the NOE specific variables.
        elif ri_label == 'NOE':
            # Misc.
            self.noe_inc = self.noe_inc + 1
            ri_inc = self.noe_inc
            label = 'NOE'

            # Tag categories.
            if self.HeteronuclNOEList:
                tag_cat = self.HeteronuclNOEList + '.'

        # Initialise the save frame.
        frame = SaveFrame(title='heteronuclear_'+label+'_list_'+`ri_inc`)

        # The save frame category.
        frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SfCategory], tagvalues=[[label+'_relaxation']]))

        # Sample info.
        frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SampleLabel], tagvalues=[['$sample_1']]))
        frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SampleConditionListLabel], tagvalues=[['$conditions_1']]))

        # NMR info.
        frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.SpectrometerFrequency1H], tagvalues=[[str(frq/1e6)]]))
        if label == 'T1':
            frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.T1CoherenceType], tagvalues=[[coherence]]))
            frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.T1ValUnits], tagvalues=[['1/s']]))
        elif label == 'T2':
            frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.T2CoherenceType], tagvalues=[[coherence]]))
            frame.tagtables.append(TagTable(free=True, tagnames=[tag_cat + self.T2ValUnits], tagvalues=[['1/s']]))

        # The relaxation tag names.
        tag_names = ['_Residue_seq_code', '_Residue_label', '_Atom_name', '_'+label+'_value', '_'+label+'_value_error']

        # Add the data.
        table = TagTable(tagnames=tag_names, tagvalues=[res_nums, res_names, atom_names, data, errors])

        # Add the tag table to the save frame.
        frame.tagtables.append(table)

        # Add the relaxation data save frame.
        self.datanodes.append(frame)
