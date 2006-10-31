###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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
from string import split


class Pymol:
    def __init__(self, relax):
        """Class containing the functions for viewing molecules."""

        self.relax = relax

        # Initialise the command history (for reopening Molmol pipes).
        self.clear_history()


    def clear_history(self):
        """Function for clearing the Molmol command history."""

        self.command_history = ""


    def command(self, run, command):
        """Function for sending Molmol commands to the program pipe."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Pass the command to Molmol.
        self.pipe_write(command)


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
        """Function for opening the PDB file in PyMOL."""

        # Argument.
        if run:
            self.run = run

        # Test if the pipe is open.
        if not self.pipe_open_test():
            return

        # Reinitialise PyMOL.
        self.pipe_write("reinitialise")

        # Open the PDB file.
        self.pipe_write("load " + self.relax.data.pdb[self.run].file_name)


    def pipe_open(self):
        """Function for opening a PyMOL pipe."""

        # Test that the PyMOL binary exists.
        self.relax.IO.test_binary('pymol')

        # Open the PyMOL pipe.
        self.relax.data.pymol = popen("pymol -qpK", 'w', 0)

        # Execute the command history.
        if len(self.command_history) > 0:
            self.pipe_write(self.command_history, store_command=0)
            return

        # Test if the PDB file has been loaded.
        if hasattr(self.relax.data, 'pdb') and self.relax.data.pdb.has_key(self.run):
            self.open_pdb()


    def pipe_open_test(self):
        """Function for testing if the PyMOL pipe is open."""

        # Test if a pipe has been opened.
        if not hasattr(self.relax.data, 'pymol'):
            return 0

        # Test if the pipe has been broken.
        try:
            self.relax.data.pymol.write('\n')
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
        self.relax.data.pymol.write(command + '\n')

        # Place the command in the command history.
        if store_command:
            self.command_history = self.command_history + command + "\n"


    def ribbon(self, run=None):
        """Apply the Molmol ribbon style."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Calculate the protons.
        self.pipe_write("CalcAtom 'H'")
        self.pipe_write("CalcAtom 'HN'")

        # Calculate the secondary structure.
        self.pipe_write("CalcSecondary")

        # Execute the ribbon macro.
        self.pipe_write("XMacStand ribbon.mac")


    def tensor_pdb(self, run=None, file=None):
        """Display the diffusion tensor geometric structure."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # To overlay the structure with the diffusion tensor, select all and reorient to the PDB frame.
        self.pipe_write("SelectAtom ''")
        self.pipe_write("SelectBond ''")
        self.pipe_write("SelectAngle ''")
        self.pipe_write("SelectDist ''")
        self.pipe_write("SelectPrim ''")
        self.pipe_write("RotateInit")
        self.pipe_write("MoveInit")

        # Read in the tensor PDB file and force Molmol to recognise the CONECT records (not that it will show the bonds)!
        self.pipe_write("ReadPdb " + file)
        file_parts = split(file, '.')
        self.pipe_write("SelectMol '@" + file_parts[0] + "'")
        self.pipe_write("CalcBond 1 1 1")

        # Apply the 'ball/stick' style to the tensor.
        self.pipe_write("SelectAtom '0'")
        self.pipe_write("SelectBond '0'")
        self.pipe_write("SelectAtom ':TNS'")
        self.pipe_write("SelectBond ':TNS'")
        self.pipe_write("XMacStand ball_stick.mac")

        # Touch up.
        self.pipe_write("RadiusAtom 1")
        self.pipe_write("SelectAtom ':TNS@C*'")
        self.pipe_write("RadiusAtom 1.5")


    def view(self, run=None):
        """Function for running Molmol."""

        # Arguments.
        self.run = run

        # Open a PyMOL pipe.
        if self.pipe_open_test():
            raise RelaxError, "The PyMOL pipe already exists."
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
