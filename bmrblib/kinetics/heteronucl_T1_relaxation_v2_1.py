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
"""The v2.1 Heteronuclear T1 data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/htmldocs/nmr_star/dictionary_files/complete_form_v21.txt.
"""

# relax module imports.
from bmrblib.kinetics.heteronucl_T1_relaxation import HeteronuclT1Saveframe, HeteronuclT1List, HeteronuclT1Experiment, HeteronuclT1Software, T1


class HeteronuclT1Saveframe_v2_1(HeteronuclT1Saveframe):
    """The v2.1 Heteronuclear T1 data saveframe class."""

    # Class variables.
    name = 'T1'
    label = 'heteronucl_T1'
    sf_label = 'T1_relaxation'

    def add_tag_categories(self):
        """Create the v2.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(HeteronuclT1List_v2_1(self))
        self.tag_categories.append(HeteronuclT1Experiment_v2_1(self))
        self.tag_categories.append(HeteronuclT1Software_v2_1(self))
        self.tag_categories.append(T1_v2_1(self))


    def pre_ops(self):
        """Perform some saveframe specific operations prior to XML creation."""

        # The saveframe description.
        self.sf_framecode = '%s MHz heteronuclear R1 %s' % (self.frq, self.count)



class HeteronuclT1List_v2_1(HeteronuclT1List):
    """v2.1 HeteronuclT1List tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1List_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1List_v2_1, self).__init__(sf)

        # Add the tag info.
        self['Details'].tag_name =                  'Details'
        self['SampleConditionListLabel'].tag_name = 'Sample_conditions_label'
        self['SpectrometerFrequency1H'].tag_name =  'Spectrometer_frequency_1H'
        self['T1CoherenceType'].tag_name =          'T1_coherence_type'
        self['T1ValUnits'].tag_name =               'T1_value_units'
        self['TextDataFormat'].tag_name =           'Text_data_format'
        self['TextData'].tag_name =                 'Text_data'



class HeteronuclT1Experiment_v2_1(HeteronuclT1Experiment):
    """v2.1 HeteronuclT1Experiment tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1Experiment_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1Experiment_v2_1, self).__init__(sf)

        # Add the tag info.
        self['ExperimentName'].tag_name = 'Experiment_label'
        self['SampleLabel'].tag_name = 'Sample_label'



class HeteronuclT1Software_v2_1(HeteronuclT1Software):
    """v2.1 HeteronuclT1Software tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT1Software tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT1Software_v2_1, self).__init__(sf)

        # Add the tag info.
        self['SoftwareLabel'].tag_name =       'Software_label'



class T1_v2_1(T1):
    """v2.1 T1 tag category."""

    def __init__(self, sf):
        """Setup the T1_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(T1_v2_1, self).__init__(sf)

        # Change tag names.
        self['CompIndexID'].tag_name =          'Residue_seq_code'
        self['CompID'].tag_name =               'Residue_label'
        self['AtomID'].tag_name =               'Atom_name'
        self['Val'].tag_name =                  'T1_value'
        self['ValErr'].tag_name =               'T1_value_error'
