###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

from re import match
import types


class Print_all_data:
    def __init__(self, relax):
        """Class containing the macros for manipulating the program state."""

        self.relax = relax


    def __repr__(self):
        """Macro for printing all the data in self.relax.data"""

        string = ""
        # Loop over the data structures in self.relax.data
        for name in dir(self.relax.data):
            if not self.filter_data_structure(self.relax.data, name):
                string = string + "self.relax.data." + name + ":\n" + `getattr(self.relax.data, name)` + "\n\n"

        # Loop over the sequence.
        for i in range(len(self.relax.data.res)):
            string = string + "\nResidue " + `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name + "\n\n"
            for name in dir(self.relax.data.res[i]):
                if not self.filter_data_structure(self.relax.data.res[i], name):
                    string = string + "self.relax.data.res[" + `i` + "]." + name + ": " + `getattr(self.relax.data.res[i], name)` + "\n"

        return string


    def filter_data_structure(self, data, name):
        """Function to filter out unwanted data structures from self.relax.data

        If name is unwanted, 1 is returned, otherwise 0 is returned.
        """

        attrib = type(getattr(data, name))
        if match("__", name):
            return 1
        elif attrib == types.ClassType:
            return 1
        elif attrib == types.InstanceType:
            return 1
        elif attrib == types.MethodType:
            return 1
        elif attrib == types.NoneType:
            return 1
        else:
            return 0
