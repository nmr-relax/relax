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
"""The v3.1 Auto relaxation data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#auto_relaxation.
"""

# relax module imports.
from bmrblib.kinetics.auto_relaxation import AutoRelaxationSaveframe, AutoRelaxationList, AutoRelaxationExperiment, AutoRelaxationSoftware, AutoRelaxation


class AutoRelaxationSaveframe_v3_1(AutoRelaxationSaveframe):
    """The v3.1 Auto relaxation data saveframe class."""

    # Class variables.
    name = 'auto'
    sf_label = 'auto_relaxation'

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(AutoRelaxationList_v3_1(self))
        self.tag_categories.append(AutoRelaxationExperiment_v3_1(self))
        self.tag_categories.append(AutoRelaxationSoftware_v3_1(self))
        self.tag_categories.append(AutoRelaxation_v3_1(self))



class AutoRelaxationList_v3_1(AutoRelaxationList):
    """v3.1 AutoRelaxationList tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxationList_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxationList_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation_list'

        # Change tag names.
        self['SfCategory'].tag_name =               'Sf_category'
        self['SfFramecode'].tag_name =              'Sf_framecode'
        self['EntryID'].tag_name =                  'Entry_ID'
        self['AutoRelaxationListID'].tag_name =     'ID'
        self['DataFileName'].tag_name =             'Data_file_name'
        self['SampleConditionListID'].tag_name =    'Sample_condition_list_ID'
        self['SampleConditionListLabel'].tag_name = 'Sample_condition_list_label'
        self['TempCalibrationMethod'].tag_name =    'Temp_calibration_method'
        self['TempControlMethod'].tag_name =        'Temp_control_method'
        self['SpectrometerFrequency1H'].tag_name =  'Spectrometer_frequency_1H'
        self['CommonRelaxationTypeName'].tag_name = 'Common_relaxation_type_name'
        self['RelaxationCoherenceType'].tag_name =  'Relaxation_coherence_type'
        self['RelaxationValUnits'].tag_name =       'Relaxation_val_units'
        self['RelaxationValType'].tag_name =        'Relaxation_val_type'
        self['RexUnits'].tag_name =                 'Rex_units'
        self['Details'].tag_name =                  'Details'
        self['TextDataFormat'].tag_name =           'Text_data_format'
        self['TextData'].tag_name =                 'Text_data'



class AutoRelaxationExperiment_v3_1(AutoRelaxationExperiment):
    """v3.1 AutoRelaxationExperiment tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxationExperiment_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxationExperiment_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation_experiment'

        # Change tag names.
        self['ExperimentID'].tag_name =         'Experiment_ID'
        self['ExperimentName'].tag_name =       'Experiment_name'
        self['SampleID'].tag_name =             'Sample_ID'
        self['SampleLabel'].tag_name =          'Sample_label'
        self['SampleState'].tag_name =          'Sample_state'
        self['EntryID'].tag_name =              'Entry_ID'
        self['AutoRelaxationListID'].tag_name = 'Auto_relaxation_list_ID'



class AutoRelaxationSoftware_v3_1(AutoRelaxationSoftware):
    """v3.1 AutoRelaxationSoftware tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxationSoftware_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxationSoftware_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation_software'

        # Change tag names.
        self['SoftwareID'].tag_name =           'Software_ID'
        self['SoftwareLabel'].tag_name =        'Software_label'
        self['MethodID'].tag_name =             'Method_ID'
        self['MethodLabel'].tag_name =          'Method_label'
        self['EntryID'].tag_name =              'Entry_ID'
        self['AutoRelaxationListID'].tag_name = 'Auto_relaxation_list_ID'



class AutoRelaxation_v3_1(AutoRelaxation):
    """v3.1 AutoRelaxation tag category."""

    def __init__(self, sf):
        """Setup the AutoRelaxation_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(AutoRelaxation_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Auto_relaxation'

        # Change tag names.
        self['AutoRelaxationID'].tag_name =     'ID'
        self['AssemblyID'].tag_name =           'Assembly_ID'
        self['AssemblyAtomID'].tag_name =       'Assembly_atom_ID'
        self['EntityAssemblyID'].tag_name =     'Entity_assembly_ID'
        self['EntityID'].tag_name =             'Entity_ID'
        self['CompIndexID'].tag_name =          'Comp_index_ID'
        self['SeqID'].tag_name =                'Seq_ID'
        self['CompID'].tag_name =               'Comp_ID'
        self['AtomID'].tag_name =               'Atom_ID'
        self['AtomType'].tag_name =             'Atom_type'
        self['AtomIsotopeNumber'].tag_name =    'Atom_isotope_number'
        self['Val'].tag_name =                  'Auto_relaxation_val'
        self['ValErr'].tag_name =               'Auto_relaxation_val_err'
        self['RexVal'].tag_name =               'Rex_val'
        self['RexErr'].tag_name =               'Rex_err'
        self['ResonanceID'].tag_name =          'Resonance_ID'
        self['AuthEntityAssemblyID'].tag_name = 'Auth_entity_assembly_ID'
        self['AuthSeqID'].tag_name =            'Auth_seq_ID'
        self['AuthCompID'].tag_name =           'Auth_comp_ID'
        self['AuthAtomID'].tag_name =           'Auth_atom_ID'
        self['EntryID'].tag_name =              'Entry_ID'
        self['AutoRelaxationListID'].tag_name = 'Auto_relaxation_list_ID'
