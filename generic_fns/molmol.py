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

from os import popen


class Molmol:
    def __init__(self, relax):
        """Class containing the functions for viewing molecules."""

        self.relax = relax

        # Initialise the command history (for reopening Molmol pipes).
        self.clear_history()


    def clear_history(self):
        """Function for clearing the Molmol command history."""

        self.command_history = ""


    def open_pipe(self):
        """Function for opening a Molmol pipe."""

        # Open the Molmol pipe.
        self.relax.data.molmol = popen("molmol -f -", 'w', 0)

        # Execute the command history.
        if len(self.command_history) > 0:
            self.write(self.command_history, store_command=0)
            return

        # Test if the PDB file has been loaded.
        if hasattr(self.relax.data, 'pdb'):
            self.open_pdb()

        # Run InitAll to remove everything from molmol.
        else:
            self.write("InitAll yes")


    def open_pdb(self, run=None):
        """Function for opening the PDB file in Molmol."""

        # Argument.
        if run:
            self.run = run

        # Test if the pipe is open.
        if not self.pipe_open():
            return

        # Run InitAll to remove everything from molmol.
        self.write("InitAll yes")

        # Open the PDB.
        self.write("ReadPdb " + self.relax.data.pdb[self.run].file_name)


    def pipe_open(self):
        """Function for testing if the Molmol pipe is open."""

        # Test if a pipe has been opened.
        if not hasattr(self.relax.data, 'molmol'):
            return 0

        # Test if the pipe has been broken.
        try:
            self.relax.data.molmol.write('\n')
        except IOError:
            return 0

        # The pipe is open.
        return 1


    def view(self, run=None):
        """Function for running Molmol."""

        # Arguments.
        self.run = run

        # Open a Molmol pipe.
        if self.pipe_open():
            raise RelaxError, "The Molmol pipe already exists."
        else:
            self.open_pipe()


    def write(self, command=None, store_command=1):
        """Function for writing to the Molmol pipe.

        This function is also used to execute a user supplied Molmol command.
        """

        # Reopen the pipe if needed.
        if not self.pipe_open():
            self.open_pipe()

        # Write the command to the pipe.
        self.relax.data.molmol.write(command + '\n')

        # Place the command in the command history.
        if store_command:
            self.command_history = self.command_history + command + "\n"
