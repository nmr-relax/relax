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
from bmrblib.experimental_details.software import SoftwareSaveframe, Software, SoftwareCitation, Task, Vendor


class SoftwareSaveframe_v3_1(SoftwareSaveframe):
    """The software saveframe class."""

    # Class variables.
    sf_label = 'software'

    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.tag_categories.append(Software_v3_1(self))
        self.tag_categories.append(SoftwareCitation_v3_1(self))
        self.tag_categories.append(Task_v3_1(self))
        self.tag_categories.append(Vendor_v3_1(self))



class Software_v3_1(Software):
    """Base class for the Software tag category."""

    def __init__(self, sf):
        """Setup the Software tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Software_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Software'

        # Change tag names.
        self['SfCategory'].tag_name = 'Sf_category'
        self['SfFramecode'].tag_name = 'Sf_framecode'



class SoftwareCitation_v3_1(SoftwareCitation):
    """Base class for the SoftwareCitation tag category."""


    def __init__(self, sf):
        """Setup the SoftwareCitation tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(SoftwareCitation_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Software_citation'



class Task_v3_1(Task):
    """Base class for the Task tag category."""

    def __init__(self, sf):
        """Setup the Task tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Task_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Task'



class Vendor_v3_1(Vendor):
    """Base class for the Vendor tag category."""

    def __init__(self, sf):
        """Setup the Vendor tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(Vendor_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Vendor'
