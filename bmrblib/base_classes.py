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

# relax module imports.
from bmrblib.misc import translate
from bmrblib.pystarlib.TagTable import TagTable


class BaseSaveframe:
    """The base class for the saveframe classes."""

    def generate_data_ids(self, N):
        """Generate the data ID structure.

        @keyword N: The number of data points.
        @type N:    int
        """

        # The data ID values.
        self.data_ids = translate(range(1, N+1))



class TagCategory:
    """The base class for tag category classes."""

    def __init__(self, sf):
        """Initialise the tag category object, placing the saveframe into its namespace.

        @param sf:                      The saveframe object.
        @type sf:                       saveframe instance
        """

        # Place the saveframe and tag info into the namespace.
        self.sf = sf

        # The tag name dictionary.
        self.tag_names = {}
        self.tag_names_full = {}

        # The specific variables dictionary.
        self.variables = {}

        # Set up the tag information.
        self.tag_setup()

        # Generate the full names.
        for key, name in self.tag_names.items():
            self.tag_names_full[key] = self.create_tag_label(name) 


    def create_tag_label(self, tag_name):
        """Generate the full NMR-STAR tag name.

        @param tag_name:    The name of the tag, without the tag category label prefix.
        @type tag_name:     str
        """

        # The full tag name.
        if tag_name:
            return self.tag_category_label_full + tag_name


    def create_tag_table(self, info, free=False):
        """Create and return a tag table based on the info structure.

        @param info:    The key and object pair list.  This consists of the keys of
                        self.tag_names being the first element and the names of the objects being
                        the second element, both of the second dimension.  The fist dimension are
                        the different pairs.
        @type info:     list of list of str
        @keyword free:  Flag to create a free STAR table.
        @type free:     bool
        @return:        The tag table.
        @rtype:         TagTable instance
        """

        # Init.
        keys = list(self.tag_names.keys())
        tag_names = []
        tag_values = []

        # Loop over the keys and object names of the info structure.
        for key, name in info:
            # Key check.
            if key not in keys:
                raise NameError("The key '%s' is not located in the self.tag_names structure." % key)

            # The tag names and values (skipping empty entries in self.tag_names).
            if self.tag_names[key] != None:
                tag_names.append(self.tag_names_full[key])
                tag_values.append(getattr(self.sf, name))

        # Add the data and return the table.
        return TagTable(free=free, tagnames=tag_names, tagvalues=tag_values)


    def tag_setup(self, tag_category_label=None, sep=None):
        """Setup the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Place the args into the class namespace.
        self.tag_category_label = tag_category_label
        if sep:
            self.sep = sep
        else:
            self.sep = '.'

        # Create the full tag label.
        self.tag_category_label_full = '_'
        if self.tag_category_label:
            self.tag_category_label_full = self.tag_category_label_full + self.tag_category_label + self.sep
