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
"""The v2.1 Heteronuclear NOE data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/htmldocs/nmr_star/dictionary_files/complete_form_v21.txt.
"""

# relax module imports.
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESaveframe, HeteronuclNOEList, HeteronuclNOEExperiment, HeteronuclNOESoftware, HeteronuclNOE


class HeteronuclNOESaveframe_v2_1(HeteronuclNOESaveframe):
    """The v2.1 Heteronuclear NOE data saveframe class."""

    # Class variables.
    name = 'Heteronuclear_NOE'
    label = 'heteronucl_NOE'
    sf_label = 'heteronuclear_NOE'

    def add_tag_categories(self):
        """Create the v2.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(HeteronuclNOEList_v2_1(self))
        self.tag_categories.append(HeteronuclNOEExperiment_v2_1(self))
        self.tag_categories.append(HeteronuclNOESoftware_v2_1(self))
        self.tag_categories.append(HeteronuclNOE_v2_1(self))


    def pre_ops(self):
        """Perform some saveframe specific operations prior to XML creation."""

        # The saveframe description.
        self.sf_framecode = '%s MHz heteronuclear NOE %s' % (self.frq, self.count)



class HeteronuclNOEList_v2_1(HeteronuclNOEList):
    """v2.1 HeteronuclNOEList tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOEList_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOEList_v2_1, self).__init__(sf)

        # Add the tag info.
        self['SampleConditionListLabel'].tag_name = 'Sample_conditions_label'
        self['SpectrometerFrequency1H'].tag_name =  'Spectrometer_frequency_1H'
        self['HeteronuclearNOEValType'].tag_name =  'Heteronuclear_NOE_value_type'
        self['NOERefVal'].tag_name =                'NOE_reference_value'
        self['NOERefDescription'].tag_name =        'NOE_reference_description'
        self['TextDataFormat'].tag_name =           'Text_data_format'
        self['TextData'].tag_name =                 'Text_data'



class HeteronuclNOEExperiment_v2_1(HeteronuclNOEExperiment):
    """v2.1 HeteronuclNOEExperiment tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOEExperiment_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOEExperiment_v2_1, self).__init__(sf)

        # Add the tag info.
        self['ExperimentName'].tag_name = 'Experiment_label'
        self['SampleLabel'].tag_name = 'Sample_label'



class HeteronuclNOESoftware_v2_1(HeteronuclNOESoftware):
    """v2.1 HeteronuclNOESoftware tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOESoftware tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOESoftware_v2_1, self).__init__(sf)

        # Add the tag info.
        self['SoftwareLabel'].tag_name =       'Software_label'


class HeteronuclNOE_v2_1(HeteronuclNOE):
    """v2.1 HeteronuclNOE tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclNOE_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclNOE_v2_1, self).__init__(sf)

        # Change tag names.
        self['CompIndexID1'].tag_name =         'Residue_seq_code'
        self['CompID1'].tag_name =              'Residue_label'
        self['Val'].tag_name =                  'Heteronuclear_NOE_value'
        self['ValErr'].tag_name =               'Heteronuclear_NOE_value_error'
