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
"""The model_free saveframe category (used to be called order_parameters).

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#order_parameters
"""

# relax module imports.
from bmrblib.experimental_details.sample_conditions import SampleConditionsSaveframe, SampleConditionList, SampleConditionCitation, SampleConditionVariable


class SampleConditionsSaveframe_v3_1(SampleConditionsSaveframe):
    """The v3.1 sample conditions saveframe class."""

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(SampleConditionList_v3_1(self))
        self.tag_categories.append(SampleConditionCitation_v3_1(self))
        self.tag_categories.append(SampleConditionVariable_v3_1(self))


class SampleConditionList_v3_1(SampleConditionList):
    """The v3.1 SampleConditionList tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionList tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionList_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Sample_condition_list'

        # Change tag names.
        self['SfCategory'].tag_name =               'Sf_category'
        self['SfFramecode'].tag_name =              'Sf_framecode'
        self['SampleConditionListID'].tag_name =    'ID'
        self['Details'].tag_name =                  'Details'



class SampleConditionCitation_v3_1(SampleConditionCitation):
    """The v3.1 SampleConditionCitation tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionCitation tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionCitation_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Sample_condition_list'

        # Change tag names.
        self['CitationID'].tag_name =               'Citation_ID'
        self['CitationLabel'].tag_name =            'Citation_label'
        self['SampleConditionListID'].tag_name =    'Sample_condition_list_ID'



class SampleConditionVariable_v3_1(SampleConditionVariable):
    """The v3.1 SampleConditionVariable tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionVariable tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionVariable_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Sample_condition_variable'

        # Change tag names.
        self['Type'].tag_name =                     'Type'
        self['Val'].tag_name =                      'Val'
        self['ValErr'].tag_name =                   'Val_err'
        self['ValUnits'].tag_name =                 'Val_units'
        self['SampleConditionListID'].tag_name =    'Sample_condition_list_ID'
