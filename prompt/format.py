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


from generic_functions import Generic_functions
from select_res import Select_res


class Skin:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the macro class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the macro class data
        structures are accessible.  For more flexibility use the macro class directly.
        """

        # Load the macro class into the namespace of this __init__ function.
        x = Macro_class(relax)

        # Place references to the interactive functions within the namespace of this skin class.
        self.format = x.format
        self.print_data = x.print_data


class Macro_class(Generic_functions, Select_res):
    def __init__(self, relax):
        """Macros for printing data to standard out."""

        self.relax = relax


    def format(self, *args):
        """Macro to print the names of all data structures in self.relax.data

        With no arguments, the names of all data structures in self.relax.data are printed
        along with the data type.


        FIN
        """

        self.args = args

        # Print the names of all data structures in self.relax.data if no arguments are given.
        if len(self.args) == 0:
            print "Data structures:"
            for name in dir(self.relax.data):
                if not self.filter_data_structure(name):
                    print "   " + name + " " + `type(getattr(self.relax.data, name))`
            return

        # Sort out the arguments.
        self.struct = self.args[0]
        self.sel = self.args[1:]

        # Test if the data structure exists.
        try:
            getattr(self.relax.data, self.struct)
        except AttributeError:
            print "Data structure 'self.relax.data." + self.struct + "' does not exist."
            return

        # Sequence data.
        if self.struct == 'seq':
            # Test if sequence data is loaded.
            try:
                self.relax.data.seq
            except AttributeError:
                print "No sequence data loaded."
                return
            self.indecies = self.select_residues()
            if not self.indecies:
                return
            self.print_data(self.relax.data.seq, seq_flag=1)

        # Relaxation data.
        #elif self.struct == 'relax_data':
        #    self.print_data(self.relax.data.seq, seq_flag=0)

        # Other data.
        else:
            print "Data structure " + self.struct + ":"
            print `getattr(self.relax.data, self.struct)`


    def print_data(self, data, seq_flag=0):
        """Macro to print data according to the argument list given."""

        if seq_flag:
            print "%-5s%-5s" % ("num", "name")
        else:
            print "%-5s%-5s%-20s%-20s" % ("num", "name", "data", "errors")

        for index in self.indecies:
            if seq_flag:
                print "%-5i%-5s" % (data[index][0], data[index][1])
            else:
                print "%-5i%-5s%-20e%-20e" % (data[index][0], data[index][1], data[index][2], data[index][3])
