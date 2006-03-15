###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from math import pi
from re import match
from types import DictType, ListType


# Global data.
##############

class Data:
    def __init__(self):
        """Class containing all the program data."""

        # Fundamental constants.
        #self.h = 6.6260755e-34    # Old low precision value.
        self.h = 6.62606876e-34
        self.h_bar = self.h / ( 2.0*pi )
        self.mu0 = 4.0 * pi * 1e-7

        # PDB data.
        self.pdb = SpecificData()

        # Diffusion data.
        self.diff = SpecificData()

        # The residue specific data.
        self.res = Residue()

        # The name of the runs.
        self.run_names = []

        # The type of the runs.
        self.run_types = []

        # Global minimisation statistics.
        self.chi2 = {}
        self.iter = {}
        self.f_count = {}
        self.g_count = {}
        self.h_count = {}
        self.warning = {}



    def __repr__(self):
        text = "The data class containing all permanent program data.\n"
        text = text + "The class contains the following objects:\n"
        for name in dir(self):
            if match("^__", name):
                continue
            text = text + "  " + name + ", " + `type(getattr(self, name))` + "\n"
        return text



# Empty data container.
#######################

class Element:
    def __init__(self):
        """Empty data container."""


    def __repr__(self):
        # Header.
        text = "%-25s%-100s\n\n" % ("Data structure", "Value")

        # Data structures.
        for name in dir(self):
            if match("^__", name):
                continue
            text = text + "%-25s%-100s\n" % (name, `getattr(self, name)`)

        # Return the lot.
        return text


# Specific data class.
######################

class SpecificData(DictType):
    def __init__(self):
        """Dictionary type class for specific data."""


    def __repr__(self):
        text = "Data:\n"
        if len(self) == 0:
            text = text + "  {}\n"
        else:
            i = 0
            for key in self.keys():
                if i == 0:
                    text = text + "  { "
                else:
                    text = text + "  , "
                text = text + "Key " + `key` + ":\n"
                for name in dir(self[key]):
                    if match("^__", name):
                        continue
                    text = text + "    " + name + ", " + `type(getattr(self[key], name))` + "\n"
                i = i + 1
            text = text + "  }\n"

        return text


    def add_item(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = Element()



# Residue specific data.
########################

class Residue(DictType):
    def __init__(self):
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
            text = text + "\nThese can be accessed by typing 'self.relax.data.res[key]'.\n"

        return text


    def add_list(self, key):
        """Function for adding an empty container to the dictionary."""

        self[key] = ResidueList()


class ResidueList(ListType):
    def __init__(self):
        """Empty data container for residue specific data."""


    def __repr__(self):
        text = "Sequence data.\n\n"
        text = text + "%-8s%-8s%-8s%-10s" % ("Index", "Number", "Name", "Selected") + "\n"
        for i in xrange(len(self)):
            text = text + "%-8i%-8i%-8s%-10i" % (i, self[i].num, self[i].name, self[i].select) + "\n"
        text = text + "\nThese can be accessed by typing 'self.relax.data.res[key][index]'.\n"
        return text


    def add_item(self):
        """Function for appending an empty container to the list."""

        self.append(ResidueElement())


class ResidueElement(object):
    def __init__(self):
        """Empty container for residue specific data for a single residue."""

        self.userSelect = 1


    def autoSelect(self):
        """Function to automatically deselect residues lacking relax_data"""

        if not hasattr(self, 'relax_data'):
            return 0

        if hasattr(self, 'params'):
            if len(self.params) < len(self.relax_data):
                return 0

        return 1


    def __getattr__(self, name):
        """Force on-the-fly evaluation of select every time it is referenced"""

        # The list of data maps.
        if name == 'select':
            return (self.autoSelect() and self.userSelect)
        raise AttributeError, name


    def __repr__(self):
        # Header.
        text = "%-25s%-100s\n\n" % ("Data structure", "Value")

        # Data structures.
        for name in dir(self):
            if match("^__", name):
                continue
            if name == 'autoSelect' or name == 'userSelect':
                continue
            text = text + "%-25s%-100s\n" % (name, `getattr(self, name)`)

        text = text + "%-25s%-100s\n" % ('select', `getattr(self, 'select')`)

        # Return the lot.
        return text


    def __setattr__(self, name, value):
        """Prevent accidental rebinding of select."""

        # The list of prescribed attributes.
        dontRebind = ['select', 'autoSelect']
        if name in dontRebind:

            # Allow initial binding of the attribute.
            if not hasattr(self, name):
                self.__dict__[name] = value

            # But prevent rebinding.
            else:
                raise AttributeError, """Can't rebind automated residue selection. Use userSelect instead (do select.res())"""

        # Normal behaviour for attributes not in list.
        self.__dict__[name] = value

