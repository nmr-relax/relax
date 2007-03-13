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




# The spin system data.
#######################

class SpinContainer:
    """Class containing all the spin system specific data."""

    def __init__(self, spin_name=None, spin_num=None, select=1):
        """Set up the default objects of the spin system data container."""

        # The spin system name and number.
        self.name = spin_name
        self.num = spin_num
        self.select = select


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the spin system specific data.\n\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Spin systems.
            if name == 'spin':
                text = text + "  spin: The list of spin systems of the residues\n"

            # Skip certain objects.
            if match("^_", name) or name == 'spin':
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


class SpinList(ListType):
    """List type data container for spin system specific data."""

    def __init__(self):
        """Set up the first spin system data container."""

        # Add the initial spin system container at index 0.
        self.append(SpinContainer())


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Spin systems.\n\n"

        # Residue data.
        text = text + "%-8s%-8s%-8s%-10s" % ("Index", "Number", "Name", "Selected") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s%-8s%-10i" % (i, `self[i].num`, self[i].name, self[i].select) + "\n"
        text = text + "\nThese can be accessed by typing 'D.mol[i].res[j].spin[k]', where D is the relax data storage object.\n"

        return text


    def add_item(self, spin_name=None, spin_num=None, select=1):
        """Function for appending an empty container to the list."""

        self.append(SpinContainer(spin_name, spin_num, select))



# The residue data.
###################

class ResidueContainer:
    """Class containing all the residue specific data."""

    def __init__(self, res_name=None, res_num=None):
        """Set up the default objects of the residue data container."""

        # The residue name and number.
        self.name = res_name
        self.num = res_num

        # The empty spin system list.
        self.spin = SpinList()


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the residue specific data.\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Spin systems.
            if name == 'spin':
                text = text + "  spin: The list of spin systems of the residues\n"

            # Skip certain objects.
            if match("^_", name) or name == 'spin':
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


class ResidueList(ListType):
    """List type data container for residue specific data."""

    def __init__(self):
        """Set up the first residue data container."""

        # Add the initial residue container at index 0.
        self.append(ResidueContainer())


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Residues.\n\n"

        # Residue data.
        text = text + "%-8s%-8s%-8s" % ("Index", "Number", "Name") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s%-8s" % (i, `self[i].num`, self[i].name) + "\n"
        text = text + "\nThese can be accessed by typing 'D.mol[i].res[j]', where D is the relax data storage object.\n"

        return text


    def add_item(self, res_name=None, res_num=None):
        """Function for appending an empty container to the list."""

        self.append(ResidueContainer(res_name, res_num))



# The molecule data.
###################

class MoleculeContainer:
    """Class containing all the molecule specific data."""

    def __init__(self, mol_name=None):
        """Set up the default objects of the molecule data container."""

        # The name of the molecule, corresponding to that of the structure file if specified.
        self.name = mol_name

        # The empty residue list.
        self.res = ResidueList()


    def __repr__(self):
        """The string representation of the object.

        Rather than using the standard Python conventions (either the string representation of the
        value or the "<...desc...>" notation), a rich-formatted description of the object is given.
        """

        # Intro.
        text = "Class containing all the molecule specific data.\n"

        # Objects.
        text = text + "\n"
        text = text + "Objects:\n"
        for name in dir(self):
            # Residue list.
            if name == 'res':
                text = text + "  res: The list of the residues of the molecule\n"

            # Skip certain objects.
            if match("^_", name) or name == 'res':
                continue

            # Add the object's attribute to the text string.
            text = text + "  " + name + ": " + `getattr(self, name)` + "\n"

        return text


class MoleculeList(ListType):
    """List type data container for the molecule specific data."""

    def __init__(self):
        """Set up the first molecule data container."""

        # Add the initial molecule container at index 0.
        self.append(MoleculeContainer())


    def __repr__(self):
        text = "Molecules.\n\n"
        text = text + "%-8s%-8s" % ("Index", "Name") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8s" % (i, self[i].name) + "\n"
        text = text + "\nThese can be accessed by typing 'D.mol[i]', where D is the relax data storage object.\n"
        return text


    def add_item(self, mol_name=None):
        """Function for appending an empty container to the list."""

        self.append(MoleculeContainer(mol_name))
