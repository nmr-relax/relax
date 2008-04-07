###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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

# Python module imports.
from os import popen
from string import split

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxImplementError, RelaxNoPipeError, RelaxNoSequenceError
from relax_io import file_root


class Pymol:
    """Data container for storing PyMOL related data.

    This includes information such as the PyMOL command history.  Also stored is the file handle to
    the PyMOL child process pipe.
    """

    command_history = ""
    """Variable for storing the pymol command history."""

    pipe = None
    """Writable pipe (file handle) to the PyMOL child process."""


    def clear_history(self):
        """Method for clearing the PyMOL command history."""

        self.command_history = ""


    def pipe_open(self):
        """Function for opening a PyMOL pipe."""

        # Test that the PyMOL binary exists.
        self.relax.IO.test_binary('pymol')

        # Open the PyMOL pipe.
        self.pymol = popen("pymol -qpK", 'w', 0)

        # Execute the command history.
        if len(pymol_data.command_history) > 0:
            self.pipe_write(pymol_data.command_history, store_command=0)
            return

        # Test if the PDB file has been loaded.
        if hasattr(relax_data_store, 'pdb') and relax_data_store.pdb.has_key(self.run):
            self.open_pdb()


    def pipe_open_test(self):
        """Function for testing if the PyMOL pipe is open."""

        # Test if a pipe has been opened.
        if not hasattr(self, 'pymol'):
            return 0

        # Test if the pipe has been broken.
        try:
            self.pymol.write('\n')
        except IOError:
            return 0

        # The pipe is open.
        return 1


    def pipe_write(self, command=None, store_command=1):
        """Function for writing to the PyMOL pipe.

        This function is also used to execute a user supplied PyMOL command.
        """

        # Reopen the pipe if needed.
        if not self.pipe_open_test():
            self.pipe_open()

        # Write the command to the pipe.
        self.pymol.write(command + '\n')

        # Place the command in the command history.
        if store_command:
            pymol_data.command_history = pymol_data.command_history + command + "\n"



# Initialise the Pymol data container.
pymol_data = Pymol()
"""Pymol data container instance."""



def cartoon():
    """Apply the PyMOL cartoon style and colour by secondary structure."""

    # Test if the current data pipe exists.
    if not relax_data_store.current_pipe:
        raise RelaxNoPipeError

    # Identifier.
    pdb_file = relax_data_store[relax_data_store.current_pipe].structure.file_name()
    id = file_root(pdb_file)

    # Hide everything.
    self.pipe_write("cmd.hide('everything'," + `id` + ")")

    # Show the cartoon style.
    self.pipe_write("cmd.show('cartoon'," + `id` + ")")

    # Colour by secondary structure.
    self.pipe_write("util.cbss(" + `id` + ", 'red', 'yellow', 'green')")


def command(run, command):
    """Function for sending PyMOL commands to the program pipe."""

    # Arguments.
    self.run = run

    # Test if the run exists.
    if not self.run in relax_data_store.run_names:
        raise RelaxNoPipeError, self.run

    # Pass the command to PyMOL.
    self.pipe_write(command)


def create_macro():
    """Function for creating an array of PyMOL commands."""

    # Function type.
    self.function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]

    # Specific PyMOL macro creation function.
    pymol_macro = self.relax.specific_setup.setup('pymol_macro', self.function_type)

    # Get the macro.
    self.commands = pymol_macro(self.run, self.data_type, self.style, self.colour_start, self.colour_end, self.colour_list)


def macro_exec(run=None, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Function for executing a PyMOL macro."""

    # Arguments.
    self.run = run
    self.data_type = data_type
    self.style = style
    self.colour_start = colour_start
    self.colour_end = colour_end
    self.colour_list = colour_list

    # No coded yet.
    raise RelaxImplementError

    # Test if the run exists.
    if not self.run in relax_data_store.run_names:
        raise RelaxNoPipeError, self.run

    # Test if the sequence data is loaded.
    if not relax_data_store.res.has_key(self.run):
        raise RelaxNoSequenceError, self.run

    # Create the macro.
    self.create_macro()

    # Loop over the commands and execute them.
    for command in self.commands:
        self.pipe_write(command)


def open_pdb(run=None):
    """Function for opening the PDB file in PyMOL."""

    # Argument.
    if run:
        self.run = run

    # Test if the pipe is open.
    if not self.pipe_open_test():
        return

    # Reinitialise PyMOL.
    self.pipe_write("reinitialize")

    # Open the PDB file.
    self.pipe_write("load " + relax_data_store.pdb[self.run].file_name)


def tensor_pdb(run=None, file=None):
    """Display the diffusion tensor geometric structure."""

    # Arguments.
    self.run = run

    # Test if the run exists.
    if not self.run in relax_data_store.run_names:
        raise RelaxNoPipeError, self.run

    # Read in the tensor PDB file.
    self.pipe_write("load " + file)


    # Centre of mass.
    #################

    # Select the COM residue.
    self.pipe_write("select resn COM")

    # Show the centre of mass as the dots representation.
    self.pipe_write("show dots, 'sele'")

    # Colour it blue.
    self.pipe_write("color blue, 'sele'")


    # The diffusion tensor axes.
    ############################

    # Select the AXS residue.
    self.pipe_write("select resn AXS")

    # Hide everything.
    self.pipe_write("hide ('sele')")

    # Show as 'sticks'.
    self.pipe_write("show sticks, 'sele'")

    # Colour it cyan.
    self.pipe_write("color cyan, 'sele'")

    # Select the N atoms of the AXS residue (used to display the axis labels).
    self.pipe_write("select (resn AXS and elem N)")

    # Label the atoms.
    self.pipe_write("label 'sele', name")



    # Monte Carlo simulations.
    ##########################

    # Select the SIM residue.
    self.pipe_write("select resn SIM")

    # Colour it.
    self.pipe_write("colour cyan, 'sele'")


    # Clean up.
    ###########

    # Remove the selection.
    self.pipe_write("cmd.delete('sele')")


def vector_dist(run=None, file=None):
    """Display the XH bond vector distribution.

    @param run:     The run
    @type run:      str
    @param file:    The vector distribution PDB file.
    @type file:     str
    """

    # Arguments.
    self.run = run

    # Test if the run exists.
    if not self.run in relax_data_store.run_names:
        raise RelaxNoPipeError, self.run

    # The file root.
    id = file_root(file)

    # Read in the vector distribution PDB file.
    self.pipe_write("load " + file)


    # Create a surface.
    ###################

    # Select the vector distribution.
    self.pipe_write("cmd.show('surface', " + `id` + ")")


def view(run=None):
    """Function for running PyMOL."""

    # Arguments.
    self.run = run

    # Open a PyMOL pipe.
    if self.pipe_open_test():
        raise RelaxError, "The PyMOL pipe already exists."
    else:
        self.pipe_open()


def write(run=None, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir=None, force=0):
    """Function for creating a PyMOL macro."""

    # Arguments.
    self.run = run
    self.data_type = data_type
    self.style = style
    self.colour_start = colour_start
    self.colour_end = colour_end
    self.colour_list = colour_list

    # No coded yet.
    raise RelaxImplementError

    # Test if the run exists.
    if not self.run in relax_data_store.run_names:
        raise RelaxNoPipeError, self.run

    # Test if the sequence data is loaded.
    if not relax_data_store.res.has_key(self.run):
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
