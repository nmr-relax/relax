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
"""The citations saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#citations.
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree
from bmrblib.citations.citations import CitationsSaveframe, Citations, CitationsAuthor


class CitationsSaveframe_v3_1(CitationsSaveframe):
    """The citations saveframe class."""

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(Citations_v3_1(self))
        self.tag_categories.append(CitationsAuthor_v3_1(self))



class Citations_v3_1(Citations):
    """Base class for the Citations tag category."""

    def __init__(self, sf):
        """Setup the Citations tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Citations_v3_1, self).__init__(sf)

        # The tag category label.
        self.tag_category_label = 'Citation'

        # Change tag names.
        self['SfCategory'].tag_name = 'Sf_category'
        self['SfFramecode'].tag_name = 'Sf_framecode'

        # Change variables.
        self['SfFramecode'].tag_name = 'citation_label'




class CitationsAuthor_v3_1(CitationsAuthor):
    """Base class for the CitationsAuthor tag category."""

    def __init__(self, sf):
        """Setup the CitationsAuthor tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(CitationsAuthor_v3_1, self).__init__(sf)

        # The tag category label.
        self.tag_category_label = 'Citation_author'
