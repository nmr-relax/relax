#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The v3.1 Heteronuclear T1 data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_T1_relaxation.
"""

# relax module imports.
from bmrblib.kinetics.heteronucl_T1_relaxation import HeteronuclT1Saveframe, HeteronuclT1List, HeteronuclT1Experiment, HeteronuclT1Software, T1


class HeteronuclT1Saveframe_v3_1(HeteronuclT1Saveframe):
    """The v3.1 Heteronuclear T1 data saveframe class."""

    # Class variables.
    name = 'T1'
    label = 'heteronucl_T1'
    sf_label = 'heteronucl_T1_relaxation'

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(HeteronuclT1List_v3_1(self))
        self.tag_categories.append(HeteronuclT1Experiment_v3_1(self))
        self.tag_categories.append(HeteronuclT1Software_v3_1(self))
        self.tag_categories.append(T1_v3_1(self))



class HeteronuclT1List_v3_1(HeteronuclT1List):
    """v3.1 HeteronuclT1List tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1List_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1List_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Heteronucl_T1_list'

        # Change tag names.
        self['SfCategory'].tag_name =               'Sf_category'
        self['SfFramecode'].tag_name =              'Sf_framecode'
        self['HeteronuclT1ListID'].tag_name =       'ID'
        self['DataFileName'].tag_name =             'Data_file_name'
        self['SampleConditionListID'].tag_name =    'Sample_condition_list_ID'
        self['SampleConditionListLabel'].tag_name = 'Sample_condition_list_label'
        self['SpectrometerFrequency1H'].tag_name =  'Spectrometer_frequency_1H'
        self['T1CoherenceType'].tag_name =          'T1_coherence_type'
        self['T1ValUnits'].tag_name =               'T1_val_units'
        self['Details'].tag_name =                  'Details'
        self['TextDataFormat'].tag_name =           'Text_data_format'
        self['TextData'].tag_name =                 'Text_data'



class HeteronuclT1Experiment_v3_1(HeteronuclT1Experiment):
    """v3.1 HeteronuclT1Experiment tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1Experiment_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1Experiment_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Heteronucl_T1_experiment'

        # Change tag names.
        self['ExperimentID'].tag_name =         'Experiment_ID'
        self['ExperimentName'].tag_name =       'Experiment_name'
        self['SampleID'].tag_name =             'Sample_ID'
        self['SampleLabel'].tag_name =          'Sample_label'
        self['SampleState'].tag_name =          'Sample_state'
        self['EntryID'].tag_name =              'Entry_ID'
        self['HeteronuclT1ListID'].tag_name =   'Heteronucl_T1_list_ID'



class HeteronuclT1Software_v3_1(HeteronuclT1Software):
    """v3.1 HeteronuclT1Software tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1Software_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1Software_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Heteronucl_T1_software'

        # Change tag names.
        self['SoftwareID'].tag_name =           'Software_ID'
        self['SoftwareLabel'].tag_name =        'Software_label'
        self['MethodID'].tag_name =             'Method_ID'
        self['MethodLabel'].tag_name =          'Method_label'
        self['EntryID'].tag_name =              'Entry_ID'
        self['HeteronuclT1ListID'].tag_name =   'Heteronucl_T1_list_ID'



class T1_v3_1(T1):
    """v3.1 T1 tag category."""

    def __init__(self, sf):
        """Setup the T1_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(T1_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'T1'

        # Change tag names.
        self['RxID'].tag_name =                 'ID'
        self['AssemblyAtomID'].tag_name =       'Assembly_atom_ID'
        self['EntityAssemblyID'].tag_name =     'Entity_assembly_ID'
        self['EntityID'].tag_name =             'Entity_ID'
        self['CompIndexID'].tag_name =          'Comp_index_ID'
        self['SeqID'].tag_name =                'Seq_ID'
        self['CompID'].tag_name =               'Comp_ID'
        self['AtomID'].tag_name =               'Atom_ID'
        self['AtomType'].tag_name =             'Atom_type'
        self['AtomIsotopeNumber'].tag_name =    'Atom_isotope_number'
        self['Val'].tag_name =                  'Val'
        self['ValErr'].tag_name =               'Val_err'
        self['ResonanceID'].tag_name =          'Resonance_ID'
        self['AuthEntityAssemblyID'].tag_name = 'Auth_entity_assembly_ID'
        self['AuthSeqID'].tag_name =            'Auth_seq_ID'
        self['AuthCompID'].tag_name =           'Auth_comp_ID'
        self['AuthAtomID'].tag_name =           'Auth_atom_ID'
        self['EntryID'].tag_name =              'Entry_ID'
        self['HeteronuclT1ListID'].tag_name =   'Heteronucl_T1_list_ID'
