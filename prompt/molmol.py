###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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


class Molmol:
    def __init__(self, relax):
        """Class containing the Molmol functions."""

        # Place relax in the class namespace.
        self.relax = relax

        # Help.
        self.__relax_help__ = help.relax_class_help


    def clear_history(self):
        """Function for clearing the Molmol command history."""

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "molmol.clear_history()"
            print text

        # Execute the functional code.
        self.relax.generic.molmol.clear_history()


    def command(self, command):
        """Function for executing a user supplied Molmol command.

        Example
        ~~~~~~~

        relax> molmol.command("InitAll yes")
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "molmol.command("
            text = text + "command=" + `command` + ")"
            print text

        # The command argument.
        if type(command) != str:
            raise RelaxStrError, ('command', command)

        # Execute the functional code.
        self.relax.generic.molmol.write(command=command)


    def view(self):
        """Function for viewing the collection of molecules extracted from the PDB file.

        Example
        ~~~~~~~

        relax> molmol.view()
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "molmol.view()"
            print text

        # Execute the functional code.
        self.relax.generic.molmol.view()
