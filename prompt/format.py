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


import help


class Format:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class containing functions for printing data to standard out."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def format(self, *args):
        """Function to print the names of all data structures in self.__relax__.data

        With no arguments, the names of all data structures in self.__relax__.data are printed
        along with the data type.
        """

        self.args = args

        # Print the names of all data structures in self.__relax__.data if no arguments are given.
        if len(self.args) == 0:
            print "Data structures:"
            for name in dir(self.__relax__.data):
                if not self.filter_data_structure(name):
                    print "   " + name + " " + `type(getattr(self.__relax__.data, name))`
            return

        # Sort out the arguments.
        self.struct = self.args[0]
        self.sel = self.args[1:]

        # Test if the data structure exists.
        try:
            getattr(self.__relax__.data, self.struct)
        except AttributeError:
            print "Data structure 'self.__relax__.data." + self.struct + "' does not exist."
            return

        # Sequence data.
        if self.struct == 'seq':
            # Test if sequence data is loaded.
            try:
                self.__relax__.data.seq
            except AttributeError:
                print "No sequence data loaded."
                return
            self.indecies = self.select_residues()
            if not self.indecies:
                return
            self.print_data(self.__relax__.data.seq, seq_flag=1)

        # Relaxation data.
        #elif self.struct == 'relax_data':
        #    self.print_data(self.__relax__.data.seq, seq_flag=0)

        # Other data.
        else:
            print "Data structure " + self.struct + ":"
            print `getattr(self.__relax__.data, self.struct)`


    def print_data(self, data, seq_flag=0):
        """Function to print data according to the argument list given."""

        if seq_flag:
            print "%-5s%-5s" % ("num", "name")
        else:
            print "%-5s%-5s%-20s%-20s" % ("num", "name", "data", "errors")

        for index in self.indecies:
            if seq_flag:
                print "%-5i%-5s" % (data[index][0], data[index][1])
            else:
                print "%-5i%-5s%-20e%-20e" % (data[index][0], data[index][1], data[index][2], data[index][3])
