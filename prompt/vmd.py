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

import help


class Vmd:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for interfacing with VMD."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def view(self, run=None):
        """Function for viewing the collection of molecules extracted from the PDB file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run which the PDB belongs to.


        Example
        ~~~~~~~

        relax> vmd.view('m1')
        relax> vmd.view(run='pdb')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "vmd.view("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.vmd.view(run=run)
