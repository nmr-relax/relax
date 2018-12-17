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

For example, see http://www.bmrb.wisc.edu/dictionary/htmldocs/nmr_star/dictionary_files/complete_form_v21.txt
"""

# relax module imports.
from bmrblib.experimental_details.sample_conditions import SampleConditionsSaveframe, SampleConditionList, SampleConditionCitation, SampleConditionVariable


class SampleConditionsSaveframe_v2_1(SampleConditionsSaveframe):
    """The v2.1 sample conditions saveframe class."""

    def add_tag_categories(self):
        """Create the v2.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(SampleConditionList_v2_1(self))
        self.tag_categories.append(SampleConditionVariable_v2_1(self))



class SampleConditionList_v2_1(SampleConditionList):
    """The v2.1 SampleConditionList tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionList tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionList_v2_1, self).__init__(sf)

        # Change tag names.
        self['SfCategory'].tag_name = 'Saveframe_category'



class SampleConditionVariable_v2_1(SampleConditionVariable):
    """The v2.1 SampleConditionVariable tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionVariable tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionVariable_v2_1, self).__init__(sf)

        # Change tag names.
        self['Type'].tag_name =     'Variable_type'
        self['Val'].tag_name =      'Variable_value'
        self['ValErr'].tag_name =   'Variable_value_error'
        self['ValUnits'].tag_name = 'Variable_value_units'
