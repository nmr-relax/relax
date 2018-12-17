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
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class SampleConditionsSaveframe(BaseSaveframe):
    """The sample conditions saveframe class."""

    # Class variables.
    sf_label = 'sample_conditions'

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(SampleConditionList(self))
        self.tag_categories.append(SampleConditionCitation(self))
        self.tag_categories.append(SampleConditionVariable(self))


class SampleConditionList(TagCategoryFree):
    """Base class for the SampleConditionList tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionList tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionList, self).__init__(sf)

        # Add the tag info.
        self.add(key='SampleConditionListID',   var_name='count_str',   format='int')
        self.add(key='Details',                 var_name='details',     format='str')



class SampleConditionCitation(TagCategory):
    """Base class for the SampleConditionCitation tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionCitation tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionCitation, self).__init__(sf)

        # Add the tag info.
        self.add(key='CitationID',              var_name='data_ids',        format='int')
        self.add(key='CitationLabel',           var_name='citation_label',  format='str')
        self.add(key='SampleConditionListID',   var_name='count_str',       format='int')



class SampleConditionVariable(TagCategory):
    """Base class for the SampleConditionVariable tag category."""

    def __init__(self, sf):
        """Setup the SampleConditionVariable tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SampleConditionVariable, self).__init__(sf)

        # Add the tag info.
        self.add(key='Type',                    var_name='type',            format='str')
        self.add(key='Val',                     var_name='value',           format='str')
        self.add(key='ValErr',                  var_name='error',           format='str')
        self.add(key='ValUnits',                var_name='units',           format='str')
        self.add(key='SampleConditionListID',   var_name='count_str',       format='int')
