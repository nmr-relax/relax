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


from Numeric import Float64, zeros
from re import match
import types


class Generic_functions:
    def __init__(self):
        """Base class containing generic functions used by many macros."""


    def create_data(self, data):
        """Function for creating a new data structure with the data from data."""

        new_data = zeros((len(self.relax.data.seq), 3), Float64)

        j = 0
        for i in range(len(new_data)):
            if data[j][0] == self.relax.data.seq[i][0] and data[j][1] == self.relax.data.seq[i][1]:
                new_data[i, 0] = data[j][2]
                new_data[i, 1] = data[j][3]
                new_data[i, 2] = 1.0
                j = j + 1

        return new_data


    def filter_data_structure(self, name):
        """Function to filter out unwanted data structures from self.relax.data

        If name is unwanted, 1 is returned, otherwise 0 is returned.
        """

        attrib = type(getattr(self.relax.data, name))
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
