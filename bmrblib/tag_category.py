###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""The TagCategory base class."""

class TagCategory:
    """The base class for tag category classes."""

    def __init__(self, sf, tag_category_label=None, sep='.'):
        """Initialise the tag category object, placing the saveframe into its namespace.

        @param sf:                      The saveframe object.
        @type sf:                       saveframe instance
        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Place the saveframe and tag info into the namespace.
        self.sf = sf
        self.tag_category_label = tag_category_label
        self.sep = sep


    def create_tag_label(self, tag_name):
        """Generate the full NMR-STAR tag name.

        @param tag_name:    The name of the tag, without the tag category label prefix.
        @type tag_name:     str
        """

        # Create the full tag label.
        self.tag_category_label_full = ''
        if self.tag_category_label:
            self.tag_category_label_full = self.tag_category_label + self.sep

        # The full tag name.
        return self.tag_category_label_full + tag_name
