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

from generic_functions import Generic_functions


class Value(Generic_functions):
    def __init__(self, relax):
        """Class containing functions for the setting up of data structures."""

        self.relax = relax


    def init_data(self, data, type):
        """Function for initialisation of the data type."""

        # Bond length.
        if match('[Bb]ond[ -_][Ll]ength', type):
            try:
                self.relax.data.bond_length
            except AttributeError:
                self.relax.data.bond_length = self.create_data(data)
            else:
                print "The bond lengths have already been specified."
                print "To reset the values, delete the original data (self.relax.data.bond_length)."

        # CSA.
        elif match('[Cc][Ss][Aa]', type):
            try:
                self.relax.data.csa
            except AttributeError:
                self.relax.data.csa = self.create_data(data)
            else:
                print "The CSA values have already been specified."
                print "To reset the values, delete the original data (self.self.x.data.csa)."

        # Bad type.
        else:
            print "The type '" + type + "' is not supported."


    def set(self, data_type=None, val=None, err=0.0):
        """Function for setting data structure values."""

        # Test if sequence data is loaded.
        try:
            self.relax.data.seq
        except AttributeError:
            print "Sequence data has to be loaded first."
            return

        # Create a temporary data structure.
        temp = []
        for i in range(len(self.relax.data.seq)):
            temp.append([self.relax.data.seq[i][0], self.relax.data.seq[i][1], val, err])

        # Initialise the type specific data.
        self.init_data(temp, data_type)
