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
"""The software saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#software
"""

# relax module imports.
from bmrblib.base_classes import BaseSaveframe, TagCategory, TagCategoryFree


class SoftwareSaveframe(BaseSaveframe):
    """The software saveframe class."""

    # Class variables.
    sf_label = 'software'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(Software(self))
        self.tag_categories.append(SoftwareCitation(self))
        self.tag_categories.append(Task(self))
        self.tag_categories.append(Vendor(self))


    def create_title(self):
        """Create a special software saveframe title.

        @return:    The title.
        @rtype:     str
        """

        return self.name.lower() + '_' + self.sf_label + '_' + self.count_str


class Software(TagCategoryFree):
    """Base class for the Software tag category."""

    def __init__(self, sf):
        """Setup the Software tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Software, self).__init__(sf)

        # Add the tag info.
        self.add(key='SoftwareID',  tag_name='ID',      var_name='count_str')
        self.add(key='Name',        tag_name='Name',    var_name='name')
        self.add(key='Version',     tag_name='Version', var_name='version')



class SoftwareCitation(TagCategory):
    """Base class for the SoftwareCitation tag category."""


    def __init__(self, sf):
        """Setup the SoftwareCitation tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SoftwareCitation, self).__init__(sf)

        # Add the tag info.
        self.add(key='CitationID',  tag_name='Citation_ID', var_name='cite_ids')
        self.add(key='SoftwareID',  tag_name='Software_ID', var_name='count_str')



class Task(TagCategory):
    """Base class for the Task tag category."""

    def __init__(self, sf):
        """Setup the Task tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Task, self).__init__(sf)

        # Add the tag info.
        self.add(key='Task',        tag_name='Task',        var_name='task')
        self.add(key='SoftwareID',  tag_name='Software_ID', var_name='count_str')



class Vendor(TagCategory):
    """Base class for the Vendor tag category."""

    def __init__(self, sf):
        """Setup the Vendor tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Vendor, self).__init__(sf)

        # Add the tag info.
        self.add(key='Name',                tag_name='Name',                var_name='vendor_name')
        self.add(key='Address',             tag_name='Address',             var_name='vendor_address')
        self.add(key='ElectronicAddress',   tag_name='Electronic_address',  var_name='vendor_eaddress')
        self.add(key='SoftwareID',          tag_name='SoftwareID',          var_name='count_str')
