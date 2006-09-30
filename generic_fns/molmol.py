###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006 Edward d'Auvergne                                  #
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


    def create_macro(self):
        """Function for creating an array of Molmol commands."""

        # Function type.
        self.function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]

        # Specific Molmol macro creation function.
        molmol_macro = self.relax.specific_setup.setup('molmol_macro', self.function_type)

        # Get the macro.
        self.commands = molmol_macro(self.run, self.data_type, self.style, self.colour_start, self.colour_end, self.colour_list)


    def macro_exec(self, run=None, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
        """Function for executing a Molmol macro."""

        # Arguments.
        self.run = run
        self.data_type = data_type
        self.style = style
        self.colour_start = colour_start
        self.colour_end = colour_end
        self.colour_list = colour_list

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Create the macro.
        self.create_macro()

        # Loop over the commands and execute them.
        for command in self.commands:
            self.pipe_write(command)


    def open_pdb(self, run=None):
        """Function for opening the PDB file in Molmol."""

        # Argument.
        if run:
            self.run = run

        # Test if the pipe is open.
        if not self.pipe_open_test():
            return

        # Run InitAll to remove everything from molmol.
        self.pipe_write("InitAll yes")

        # Open the PDB.
        self.pipe_write("ReadPdb " + self.relax.data.pdb[self.run].file_name)


    def pipe_open(self):
        """Function for opening a Molmol pipe."""

        # Test that the Molmol binary exists.
        self.relax.IO.test_binary('molmol')

        # Open the Molmol pipe.
        self.relax.data.molmol = popen("molmol -f -", 'w', 0)

        # Execute the command history.
        if len(self.command_history) > 0:
            self.pipe_write(self.command_history, store_command=0)
            return

        # Test if the PDB file has been loaded.
        if hasattr(self.relax.data, 'pdb') and self.relax.data.pdb.has_key(self.run):
            self.open_pdb()

        # Run InitAll to remove everything from molmol.
        else:
            self.pipe_write("InitAll yes")


    def pipe_open_test(self):
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


    def pipe_write(self, command=None, store_command=1):
        """Function for writing to the Molmol pipe.

        This function is also used to execute a user supplied Molmol command.
        """

        # Reopen the pipe if needed.
        if not self.pipe_open_test():
            self.pipe_open()

        # Write the command to the pipe.
        self.relax.data.molmol.write(command + '\n')

        # Place the command in the command history.
        if store_command:
            self.command_history = self.command_history + command + "\n"


    def view(self, run=None):
        """Function for running Molmol."""

        # Arguments.
        self.run = run

        # Open a Molmol pipe.
        if self.pipe_open_test():
            raise RelaxError, "The Molmol pipe already exists."
        else:
            self.pipe_open()


    def write(self, run=None, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir=None, force=0):
        """Function for creating a Molmol macro."""

        # Arguments.
        self.run = run
        self.data_type = data_type
        self.style = style
        self.colour_start = colour_start
        self.colour_end = colour_end
        self.colour_list = colour_list

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Create the macro.
        self.create_macro()

        # File name.
        if file == None:
            file = data_type + '.mac'

        # Open the file for writing.
        file = self.relax.IO.open_write_file(file, dir, force)

        # Loop over the commands and write them.
        for command in self.commands:
            file.write(command + "\n")

        # Close the file.
        file.close()
