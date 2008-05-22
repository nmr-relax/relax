###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2006-2008 Edward d'Auvergne                        #
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

# Python module imports.
from re import match
from types import DictType, ListType



# Empty data container.
#######################

class Element:
    """Empty data container."""

    def __repr__(self):
        # Header.
        text = "%-25s%-100s\n\n" % ("Data structure", "Value")

        # Data structures.
        for name in dir(self):
            if match("^_", name):
                continue
            text = text + "%-25s%-100s\n" % (name, `getattr(self, name)`)

        # Return the lot.
        return text


    def is_empty(self):
        """Method for testing if the Element container is empty.

        @return:    True if the Element container is empty, False otherwise.
        @rtype:     bool
        """

        # An object has been added to the container.
        for name in dir(self):
            # Skip the Element methods.
            if name == 'is_empty':
                continue

            # Skip special objects.
            if match("^__", name):
                continue

            # An object has been added.
            return False

        # The Element container is empty.
        return True



# Residue specific data.
########################

class Residue(DictType):
    """Class containing all the residue specific data."""


    def __repr__(self):
        text = "Class containing all the residue specific data.\n\n"

        # Empty.
        if not len(self):
            text = text + "The class contains no data.\n"

        # Not empty.
        else:
            text = text + "The residue container contains the following keys:\n"
            for key in self:
                text = text + "    " + `key` + "\n"
            text = text + "\nThese can be accessed by typing 'ds.res[key]'.\n"

        return text


    def add_list(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = ResidueList()


class ResidueList(ListType):
    """Empty data container for residue specific data."""

    def __repr__(self):
        text = "Sequence data.\n\n"
        text = text + "%-8s%-8s%-8s%-10s" % ("Index", "Number", "Name", "Selected") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8i%-8s%-10i" % (i, self[i].num, self[i].name, self[i].select) + "\n"
        text = text + "\nThese can be accessed by typing 'ds.res[key][index]'.\n"
        return text


    def add_item(self):
        """Function for appending an empty container to the list."""

        self.append(Element())
