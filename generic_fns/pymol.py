###############################################################################
#                                                                             #
# Copyright (C) 2006-2009 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module for interfacing with PyMOL."""

# Python module imports.
from os import popen, sep

# relax module imports.
from generic_fns.mol_res_spin import exists_mol_res_spin_data
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError
from relax_io import file_root, open_write_file, test_binary
from specific_fns.setup import get_specific_fn


class Pymol:
    """Data container for storing PyMOL related data.

    This includes information such as the PyMOL command history.  Also stored is the file handle to
    the PyMOL child process pipe.
    """

    def __init__(self):
        """Class initialisation method used to set the command history and the PyMOL pipe."""

        self.command_history = ""
        """Variable for storing the pymol command history."""

        self.pipe = None
        """Writable pipe (file handle) to the PyMOL child process."""


    def clear_history(self):
        """Method for clearing the PyMOL command history."""

        self.command_history = ""


    def open_pdb(self):
        """Function for opening the PDB file in PyMOL."""

        # Test if the pipe is open.
        if not self.pipe_open_test():
            return

        # Reinitialise PyMOL.
        self.pipe_write("reinitialize")

        # Open the PDB files.
        open_files = []
        for model in cdp.structure.structural_data:
            for mol in model.mol:
                # The file path.
                file = mol.file_name
                if mol.file_path:
                    file = mol.file_path + sep + file

                # Already loaded.
                if file in open_files:
                    continue

                # Open the file in PyMOL.
                self.pipe_write("load " + file)

                # Add to the open file list.
                open_files.append(file)


    def pipe_open(self):
        """Function for opening a PyMOL pipe."""

        # Test that the PyMOL binary exists.
        test_binary('pymol')

        # Open the PyMOL pipe.
        self.pymol = popen("pymol -qpK", 'w', 0)

        # Execute the command history.
        if len(self.command_history) > 0:
            self.pipe_write(self.command_history, store_command=0)
            return

        # Test if the PDB file has been loaded.
        if hasattr(cdp, 'structure'):
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
            self.command_history = self.command_history + command + "\n"



# Initialise the Pymol data container.
pymol = Pymol()
"""Pymol data container instance."""



def cartoon():
    """Apply the PyMOL cartoon style and colour by secondary structure."""

    # Test if the current data pipe exists.
    pipes.test()

    # Test for the structure.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Loop over the PDB files.
    open_files = []
    for model in cdp.structure.structural_data:
        for mol in model.mol:
            # Identifier.
            pdb_file = mol.file_name
            if mol.file_path:
                pdb_file = mol.file_path + sep + pdb_file
            id = file_root(pdb_file)

            # Already loaded.
            if pdb_file in open_files:
                continue

            # Add to the open file list.
            open_files.append(pdb_file)

            # Hide everything.
            pymol.pipe_write("cmd.hide('everything'," + repr(id) + ")")

            # Show the cartoon style.
            pymol.pipe_write("cmd.show('cartoon'," + repr(id) + ")")

            # Colour by secondary structure.
            pymol.pipe_write("util.cbss(" + repr(id) + ", 'red', 'yellow', 'green')")


def command(command):
    """Function for sending PyMOL commands to the program pipe.

    @param command: The command to send to PyMOL.
    @type command:  str
    """

    # Pass the command to PyMOL.
    pymol.pipe_write(command)


def cone_pdb(file=None):
    """Display the cone geometric object.

    @keyword file:  The name of the file containing the cone geometric object.
    @type file:     str
    """

    # Read in the cone PDB file.
    pymol.pipe_write("load " + file)


    # The cone axis.
    ################

    # Select the AVE, AXE, and SIM residues.
    pymol.pipe_write("select (resn AVE,AXE,SIM)")

    # Show the vector as a stick.
    pymol.pipe_write("show stick, 'sele'")

    # Colour it blue.
    pymol.pipe_write("color cyan, 'sele'")

    # Select the atom used for labelling.
    pymol.pipe_write("select (resn AVE,AXE,SIM and symbol N)")

    # Hide the atom.
    pymol.pipe_write("hide ('sele')")

    # Label using the atom name.
    pymol.pipe_write("cmd.label(\"sele\",\"name\")")


    # The cone object.
    ##################

    # Select the CON residue.
    pymol.pipe_write("select (resn CON,EDG)")

    # Hide everything.
    pymol.pipe_write("hide ('sele')")

    # Show as 'sticks'.
    pymol.pipe_write("show sticks, 'sele'")

    # Colour it white.
    pymol.pipe_write("color white, 'sele'")

    # Shorten the stick width from 0.25 to 0.15.
    pymol.pipe_write("set stick_radius,0.15000")


    # Clean up.
    ###########

    # Remove the selection.
    pymol.pipe_write("cmd.delete('sele')")


def create_macro(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Function for creating an array of PyMOL commands.

    @keyword data_type:     The data type ot map to the structure.
    @type data_type:        str
    @keyword style:         The style of the macro.
    @type style:            str
    @keyword colour_start:  The starting colour of the linear gradient.
    @type colour_start:     str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end:    The ending colour of the linear gradient.
    @type colour_end:       str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:   The colour list to search for the colour names.  Can be either 'molmol'
                            or 'x11'.
    @type colour_list:      str or None
    @return:                The list of PyMOL commands.
    @rtype:                 list of str
    """

    # Specific PyMOL macro creation function.
    pymol_macro = get_specific_fn('pymol_macro', cdp.pipe_type)

    # Get the macro.
    commands = pymol_macro(data_type, style, colour_start, colour_end, colour_list)

    # Return the macro commands.
    return commands


def macro_exec(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Execute a PyMOL macro.

    @keyword data_type:     The data type ot map to the structure.
    @type data_type:        str
    @keyword style:         The style of the macro.
    @type style:            str
    @keyword colour_start:  The starting colour of the linear gradient.
    @type colour_start:     str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end:    The ending colour of the linear gradient.
    @type colour_end:       str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:   The colour list to search for the colour names.  Can be either 'molmol'
                            or 'x11'.
    @type colour_list:      str or None
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Create the macro.
    commands = create_macro(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)

    # Loop over the commands and execute them.
    for command in commands:
        pymol.pipe_write(command)


def tensor_pdb(file=None):
    """Display the diffusion tensor geometric structure.

    @keyword file:  The name of the file containing the diffusion tensor geometric object.
    @type file:     str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Read in the tensor PDB file.
    pymol.pipe_write("load " + file)


    # Centre of mass.
    #################

    # Select the COM residue.
    pymol.pipe_write("select resn COM")

    # Show the centre of mass as the dots representation.
    pymol.pipe_write("show dots, 'sele'")

    # Colour it blue.
    pymol.pipe_write("color blue, 'sele'")


    # The diffusion tensor axes.
    ############################

    # Select the AXS residue.
    pymol.pipe_write("select resn AXS")

    # Hide everything.
    pymol.pipe_write("hide ('sele')")

    # Show as 'sticks'.
    pymol.pipe_write("show sticks, 'sele'")

    # Colour it cyan.
    pymol.pipe_write("color cyan, 'sele'")

    # Select the N atoms of the AXS residue (used to display the axis labels).
    pymol.pipe_write("select (resn AXS and elem N)")

    # Label the atoms.
    pymol.pipe_write("label 'sele', name")



    # Monte Carlo simulations.
    ##########################

    # Select the SIM residue.
    pymol.pipe_write("select resn SIM")

    # Colour it.
    pymol.pipe_write("colour cyan, 'sele'")


    # Clean up.
    ###########

    # Remove the selection.
    pymol.pipe_write("cmd.delete('sele')")


def vector_dist(file=None):
    """Display the XH bond vector distribution.

    @keyword file:   The vector distribution PDB file.
    @type file:     str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # The file root.
    id = file_root(file)

    # Read in the vector distribution PDB file.
    pymol.pipe_write("load " + file)


    # Create a surface.
    ###################

    # Select the vector distribution.
    pymol.pipe_write("cmd.show('surface', " + repr(id) + ")")


def view():
    """Function for running PyMOL."""

    # Open a PyMOL pipe.
    if pymol.pipe_open_test():
        raise RelaxError("The PyMOL pipe already exists.")
    else:
        pymol.pipe_open()


def write(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir=None, force=False):
    """Create a PyMOL macro file.

    @keyword data_type:     The data type ot map to the structure.
    @type data_type:        str
    @keyword style:         The style of the macro.
    @type style:            str
    @keyword colour_start:  The starting colour of the linear gradient.
    @type colour_start:     str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end:    The ending colour of the linear gradient.
    @type colour_end:       str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:   The colour list to search for the colour names.  Can be either 'molmol'
                            or 'x11'.
    @type colour_list:      str or None
    @keyword file:          The name of the macro file to create.
    @type file:             str
    @keyword dir:           The name of the directory to place the macro file into.
    @type dir:              str
    @keyword force:         Flag which if set to True will cause any pre-existing file to be
                            overwritten.
    @type force:            bool
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Create the macro.
    commands = create_macro(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)

    # File name.
    if file == None:
        file = data_type + '.mac'

    # Open the file for writing.
    file = open_write_file(file, dir, force)

    # Loop over the commands and write them.
    for command in commands:
        file.write(command + "\n")

    # Close the file.
    file.close()
