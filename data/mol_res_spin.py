###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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


"""The molecule-residue-spin containers."""



# The molecule data.
###################

class MoleculeList(ListType):
    """Empty data container for the molecule specific data."""


    def __repr__(self):
        text = "Molecules.\n\n"
        text = text + "%-8s%-8s" % ("Index", "Name") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s" % (i, self[i].name) + "\n"
        text = text + "\nThese can be accessed by typing 'D.mol[index]', where D is the relax data storage object.\n"
        return text


    def add_item(self):
        """Function for appending an empty container to the list."""

        self.append(MoleculeContainer())


class MoleculeContainer:
    """Class containing all the molecule specific data."""

    # The name of the molecule, corresponding to that of the structure file if specified.
    name = None


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the molecule specific data.\n\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Residue list.
            if name == 'res':
                text = text + "  res: The list of the residues of the molecule is the object\n"

            # Skip certain objects.
            if match("^_", name) or name == 'res' or name == 'add_list':
                continue

            # Add the object's attribute to the text string.
            print name
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


    def add_list(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = ResidueList()



# The residue data.
###################

class ResidueList(ListType):
    """Empty data container for residue specific data."""


    def __repr__(self):
        text = "Sequence data.\n\n"
        text = text + "%-8s%-8s%-8s%-10s" % ("Index", "Number", "Name", "Selected") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8i%-8s%-10i" % (i, self[i].num, self[i].name, self[i].select) + "\n"
        text = text + "\nThese can be accessed by typing 'relax_data_store.res[key][index]'.\n"
        return text


    def add_item(self):
        """Function for appending an empty container to the list."""

        self.append(ResidueContainer())


class ResidueContainer:
    """Class containing all the residue specific data."""


    def __repr__(self):
        text = "Class containing all the residue specific data.\n\n"

        # Empty.
        if not len(self):
            text = text + "The class contains no data.\n"

        # Not empty.
        else:
            text = text + "The residue container has the following keys:\n"
            for key in self:
                text = text + "    " + `key` + "\n"
            text = text + "\nThese can be accessed by typing 'relax_data_store.res[key]'.\n"

        return text


    def add_list(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = ResidueList()



# The spin system data.
#######################

class SpinList(ListType):
    """Empty data container for spin system specific data."""


    def __repr__(self):
        text = "Spin systems.\n\n"
        text = text + "%-8s%-8s%-8s%-10s" % ("Index", "Number", "Name", "Selected") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8i%-8s%-10i" % (i, self[i].num, self[i].name, self[i].select) + "\n"
        text = text + "\nThese can be accessed by typing 'relax_data_store.res[key][index]'.\n"
        return text


    def add_item(self):
        """Function for appending an empty container to the list."""

        self.append(SpinContainer())


class SpinContainer:
    """Class containing all the spin system specific data."""


    def __repr__(self):

        # Intro.
        text = "Class containing all the spin system specific data.\n\n"

        # Empty.
        if not len(self):
            text = text + "The class contains no data.\n"

        # Not empty.
        else:
            text = text + "The spin system container has the following keys:\n"
            for key in self:
                text = text + "    " + `key` + "\n"
            text = text + "\nThese can be accessed by typing 'relax_data_store.res[key]'.\n"

        return text
