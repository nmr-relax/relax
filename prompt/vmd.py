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

import sys

import message


class Shell:
    def __init__(self, relax):
        """The class accessible to the interpreter.

        The purpose of this class is to hide the variables and functions found within the namespace
        of the main class, found below, except for those required for interactive use.  This is an
        abstraction layer designed to avoid user confusion as none of the main class data structures
        are accessible.  For more flexibility use the main class directly.
        """

        # Load the main class into the namespace of this __init__ function.
        x = Main(relax)

        # Place references to the interactive functions within the namespace of this class.
        self.view = x.view

        # __repr__.
        self.__repr__ = message.main_class


class Main:
    def __init__(self, relax):
        """Class containing the VMD functions."""

        self.relax = relax


    def view(self):
        """Function for viewing the collection of molecules extracted from the PDB file.


        Example
        ~~~~~~~

        relax> vmd.view()
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "vmd.view()"
            print text

        # Execute the functional code.
        self.relax.generic.vmd.view()
