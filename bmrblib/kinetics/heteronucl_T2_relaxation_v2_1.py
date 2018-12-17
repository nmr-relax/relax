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
"""The v2.1 Heteronuclear T2 data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/htmldocs/nmr_star/dictionary_files/complete_form_v21.txt.
"""

# relax module imports.
from bmrblib.kinetics.heteronucl_T2_relaxation import HeteronuclT2Saveframe, HeteronuclT2List, HeteronuclT2Experiment, HeteronuclT2Software, T2


class HeteronuclT2Saveframe_v2_1(HeteronuclT2Saveframe):
    """The v2.1 Heteronuclear T2 data saveframe class."""

    # Class variables.
    name = 'T2'
    label = 'heteronucl_T2'
    sf_label = 'T2_relaxation'

    def add_tag_categories(self):
        """Create the v2.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(HeteronuclT2List_v2_1(self))
        self.tag_categories.append(HeteronuclT2Experiment_v2_1(self))
        self.tag_categories.append(HeteronuclT2Software_v2_1(self))
        self.tag_categories.append(T2_v2_1(self))


    def pre_ops(self):
        """Perform some saveframe specific operations prior to XML creation."""

        # The saveframe description.
        self.sf_framecode = '%s MHz heteronuclear R1 %s' % (self.frq, self.count)



class HeteronuclT2List_v2_1(HeteronuclT2List):
    """v2.1 HeteronuclT2List tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT2List_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT2List_v2_1, self).__init__(sf)

        # Add the tag info.
        self['Details'].tag_name =                  'Details'
        self['SampleConditionListLabel'].tag_name = 'Sample_conditions_label'
        self['SpectrometerFrequency1H'].tag_name =  'Spectrometer_frequency_1H'
        self['T2CoherenceType'].tag_name =          'T2_coherence_type'
        self['T2ValUnits'].tag_name =               'T2_value_units'
        self['TextDataFormat'].tag_name =           'Text_data_format'
        self['TextData'].tag_name =                 'Text_data'



class HeteronuclT2Experiment_v2_1(HeteronuclT2Experiment):
    """v2.1 HeteronuclT2Experiment tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT2Experiment_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT2Experiment_v2_1, self).__init__(sf)

        # Add the tag info.
        self['ExperimentName'].tag_name = 'Experiment_label'
        self['SampleLabel'].tag_name = 'Sample_label'



class HeteronuclT2Software_v2_1(HeteronuclT2Software):
    """v2.1 HeteronuclT2Software tag category."""

    def __init__(self, sf):
        """Setup the HeteronuclT2Software tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(HeteronuclT2Software_v2_1, self).__init__(sf)

        # Add the tag info.
        self['SoftwareLabel'].tag_name =       'Software_label'



class T2_v2_1(T2):
    """v2.1 T2 tag category."""

    def __init__(self, sf):
        """Setup the T2_v2_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(T2_v2_1, self).__init__(sf)

        # Change tag names.
        self['CompIndexID'].tag_name =          'Residue_seq_code'
        self['CompID'].tag_name =               'Residue_label'
        self['AtomID'].tag_name =               'Atom_name'
        self['Val'].tag_name =                  'T2_value'
        self['ValErr'].tag_name =               'T2_value_error'
