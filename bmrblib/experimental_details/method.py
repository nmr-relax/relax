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
"""The method saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#method
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class MethodSaveframe(BaseSaveframe):
    """The method saveframe class."""

    # Class variables.
    sf_label = 'method'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(Method(self))
        self.tag_categories.append(MethodCitation(self))
        self.tag_categories.append(MethodFile(self))
        self.tag_categories.append(MethodParam(self))



class Method(TagCategoryFree):
    """Base class for the Method tag category."""

    def __init__(self, sf):
        """Setup the Method tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Method, self).__init__(sf)

        # Add the tag info.
        self.add(key='MethodID',    tag_name='ID',              var_name='count_str')
        self.add(key='Details',     tag_name='Details',         var_name='details')



class MethodCitation(TagCategory):
    """Base class for the MethodCitation tag category."""

    def __init__(self, sf):
        """Setup the MethodCitation tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(MethodCitation, self).__init__(sf)

        # Add the tag info.
        self.add(key='CitationID',  tag_name='Citation_ID', var_name='cite_ids')
        self.add(key='MethodID',    tag_name='Method_ID',   var_name='count_str')


    def is_empty(self):
        """Check if the citation tag category is empty.

        @return:    The state of emptiness.
        @rtype:     bool
        """

        # No citation IDs.
        if not hasattr(self.sf, 'cite_ids') or not len(self.sf.cite_ids):
            return True

        # Not empty.
        return False


class MethodFile(TagCategory):
    """Base class for the MethodFile tag category."""

    def __init__(self, sf):
        """Setup the MethodFile tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(MethodFile, self).__init__(sf)

        # Add the tag info.
        self.add(key='Name',        tag_name='Name',        var_name='file_name',       missing=False)
        self.add(key='TextFormat',  tag_name='Text_format', var_name='text_format')
        self.add(key='Text',        tag_name='Text',        var_name='file_text',       missing=False)
        self.add(key='MethodID',    tag_name='Method_ID',   var_name='count_str')



class MethodParam(TagCategory):
    """Base class for the MethodParam tag category."""

    def __init__(self, sf):
        """Setup the MethodParam tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(MethodParam, self).__init__(sf)

        # Add the tag info.
        self.add(key='FileName',    tag_name='File_name',   var_name='param_file_name')
        self.add(key='TextFormat',  tag_name='Text_format', var_name='text_format')
        self.add(key='Text',        tag_name='Text',        var_name='param_file_text')
        self.add(key='MethodID',    tag_name='Method_ID',   var_name='count_str')
