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
"""The v3.1 Heteronuclear NOE data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESaveframe, HeteronuclNOEList, HeteronuclNOEExperiment, HeteronuclNOESoftware, HeteronuclNOE


class HeteronuclNOESaveframe_v3_1(HeteronuclNOESaveframe):
    """The v3.1 Heteronuclear NOE data saveframe class."""

    # Class variables.
    sf_label = 'heteronucl_NOEs'

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(HeteronuclNOEList_v3_1(self))
        self.tag_categories.append(HeteronuclNOEExperiment_v3_1(self))
        self.tag_categories.append(HeteronuclNOESoftware_v3_1(self))
        self.tag_categories.append(HeteronuclNOE_v3_1(self))



class HeteronuclNOEList_v3_1(HeteronuclNOEList):
    """v3.1 HeteronuclNOEList tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOEList_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOEList_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Heteronucl_NOE_list'

        # Change tag names.
        self['SfCategory'].tag_name =               'Sf_category'
        self['SfFramecode'].tag_name =              'Sf_framecode'
        self['HeteronuclNOEListID'].tag_name =      'ID'
        self['DataFileName'].tag_name =             'Data_file_name'
        self['SampleConditionListID'].tag_name =    'Sample_condition_list_ID'
        self['SampleConditionListLabel'].tag_name = 'Sample_condition_list_label'
        self['SpectrometerFrequency1H'].tag_name =  'Spectrometer_frequency_1H'
        self['TempCalibrationMethod'].tag_name =    'Temp_calibration_method'
        self['TempControlMethod'].tag_name =        'Temp_control_method'
        self['HeteronuclearNOEValType'].tag_name =  'Heteronuclear_NOE_val_type'
        self['NOERefVal'].tag_name =                'NOE_ref_val'
        self['NOERefDescription'].tag_name =        'NOE_ref_description'
        self['Details'].tag_name =                  'Details'
        self['TextDataFormat'].tag_name =           'Text_data_format'
        self['TextData'].tag_name =                 'Text_data'



class HeteronuclNOEExperiment_v3_1(HeteronuclNOEExperiment):
    """v3.1 HeteronuclNOEExperiment tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOEExperiment_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOEExperiment_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Heteronucl_NOE_experiment'

        # Change tag names.
        self['ExperimentID'].tag_name =        'Experiment_ID'
        self['ExperimentName'].tag_name =      'Experiment_name'
        self['SampleID'].tag_name =            'Sample_ID'
        self['SampleLabel'].tag_name =         'Sample_label'
        self['SampleState'].tag_name =         'Sample_state'
        self['EntryID'].tag_name =             'Entry_ID'
        self['HeteronuclNOEListID'].tag_name = 'Heteronucl_NOE_list_ID'



class HeteronuclNOESoftware_v3_1(HeteronuclNOESoftware):
    """v3.1 HeteronuclNOESoftware tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOESoftware_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOESoftware_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Heteronucl_NOE_software'

        # Change tag names.
        self['SoftwareID'].tag_name =          'Software_ID'
        self['SoftwareLabel'].tag_name =       'Software_label'
        self['MethodID'].tag_name =            'Method_ID'
        self['MethodLabel'].tag_name =         'Method_label'
        self['EntryID'].tag_name =             'Entry_ID'
        self['HeteronuclNOEListID'].tag_name = 'Heteronucl_NOE_list_ID'



class HeteronuclNOE_v3_1(HeteronuclNOE):
    """v3.1 HeteronuclNOE tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOE_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOE_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Heteronucl_NOE'

        # Add the tag info.
        self['HeteronuclNOEID'].tag_name =       'ID'
        self['AssemblyAtomID1'].tag_name =       'Assembly_atom_ID_1'
        self['EntityAssemblyID1'].tag_name =     'Entity_assembly_ID_1'
        self['EntityID1'].tag_name =             'Entity_ID_1'
        self['CompIndexID1'].tag_name =          'Comp_index_ID_1'
        self['SeqID1'].tag_name =                'Seq_ID_1'
        self['CompID1'].tag_name =               'Comp_ID_1'
        self['AtomID1'].tag_name =               'Atom_ID_1'
        self['AtomType1'].tag_name =             'Atom_type_1'
        self['AtomIsotopeNumber1'].tag_name =    'Atom_isotope_number_1'
        self['AssemblyAtomID2'].tag_name =       'Assembly_atom_ID_2'
        self['EntityAssemblyID2'].tag_name =     'Entity_assembly_ID_2'
        self['EntityID2'].tag_name =             'Entity_ID_2'
        self['CompIndexID2'].tag_name =          'Comp_index_ID_2'
        self['SeqID2'].tag_name =                'Seq_ID_2'
        self['CompID2'].tag_name =               'Comp_ID_2'
        self['AtomID2'].tag_name =               'Atom_ID_2'
        self['AtomType2'].tag_name =             'Atom_type_2'
        self['AtomIsotopeNumber2'].tag_name =    'Atom_isotope_number_2'
        self['Val'].tag_name =                   'Val'
        self['ValErr'].tag_name =                'Val_err'
        self['ResonanceID1'].tag_name =          'Resonance_ID_1'
        self['ResonanceID2'].tag_name =          'Resonance_ID_2'
        self['AuthEntityAssemblyID1'].tag_name = 'Auth_entity_assembly_ID_1'
        self['AuthSeqID1'].tag_name =            'Auth_seq_ID_1'
        self['AuthCompID1'].tag_name =           'Auth_comp_ID_1'
        self['AuthAtomID1'].tag_name =           'Auth_atom_ID_1'
        self['AuthEntityAssemblyID2'].tag_name = 'Auth_entity_assembly_ID_2'
        self['AuthSeqID2'].tag_name =            'Auth_seq_ID_2'
        self['AuthCompID2'].tag_name =           'Auth_comp_ID_2'
        self['AuthAtomID2'].tag_name =           'Auth_atom_ID_2'
        self['EntryID'].tag_name =               'Entry_ID'
        self['HeteronuclNOEListID'].tag_name =   'Heteronucl_NOE_list_ID'
