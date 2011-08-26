###############################################################################
#                                                                             #
# Copyright (C) 2004-2011 Edward d'Auvergne                                   #
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
"""Module for interfacing with Molmol."""

# Python module imports.
from os import sep
from string import split
from subprocess import PIPE, Popen
from time import sleep

# relax module imports.
from generic_fns.mol_res_spin import exists_mol_res_spin_data
from generic_fns import pipes
from relax_errors import RelaxError, RelaxNoSequenceError
from relax_io import get_file_path, open_write_file, test_binary
from specific_fns.setup import get_specific_fn
from status import Status; status = Status()


class Molmol:
    """The Molmol execution object."""

    def __init__(self):
        """Set up the Molmol execution object."""

        # Variable for storing the Molmol command history.
        self.command_history = ""


    def clear_history(self):
        """Clear the Molmol command history."""

        self.command_history = ""


    def exec_cmd(self, command=None, store_command=True):
        """Write to the Molmol pipe.

        This function is also used to execute a user supplied Molmol command.


        @param command:         The Molmol command to send into the program.
        @type command:          str
        @param store_command:   A flag specifying if the command should be stored in the history
                                variable.
        @type store_command:    bool
        """

        # Reopen the pipe if needed.
        if not self.running():
            self.open_gui()

        # Write the command to the pipe.
        self.molmol.write(command + '\n')

        # Place the command in the command history.
        if store_command:
            self.command_history = self.command_history + command + "\n"


    def open_gui(self):
        """Open a Molmol pipe."""

        # Test that the Molmol binary exists.
        test_binary('molmol')

        # Open Molmol as a pipe.
        self.molmol = Popen(['molmol', '-f', '-'], stdin=PIPE).stdin

        # Execute the command history.
        if len(self.command_history) > 0:
            self.exec_cmd(self.command_history, store_command=0)
            return

        # Wait a little while for Molmol to initialise.
        sleep(2)

        # Test if the PDB file has been loaded.
        if hasattr(cdp, 'structure'):
            self.open_pdb()

        # Run InitAll to remove everything from Molmol.
        else:
            self.molmol.write("InitAll yes\n")


    def open_pdb(self):
        """Open the PDB file in Molmol."""

        # Test if Molmol is running.
        if not self.running():
            return

        # Run InitAll to remove everything from molmol.
        self.exec_cmd("InitAll yes")

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

                # Open the file in Molmol.
                self.exec_cmd("ReadPdb " + file)

                # Add to the open file list.
                open_files.append(file)


    def running(self):
        """Test if Molmol is running.

        @return:    Whether the Molmol pipe is open or not.
        @rtype:     bool
        """

        # Pipe exists.
        if not hasattr(self, 'molmol'):
            return False

        # Test if the pipe has been broken.
        try:
            self.molmol.write('\n')
        except IOError:
            import sys
            sys.stderr.write("Broken pipe")
            return False

        # Molmol is running
        return True



# Initialise the Molmol executable object.
molmol_obj = Molmol()
"""Molmol data container instance."""




def command(command):
    """Function for sending Molmol commands to the program pipe.

    @param command: The command to send into the program.
    @type command:  str
    """

    # Pass the command to Molmol.
    molmol_obj.exec_cmd(command)


def create_macro(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Create an array of Molmol commands.

    @keyword data_type:     The data type to map to the structure.
    @type data_type:        str
    @keyword style:         The style of the macro.
    @type style:            str
    @keyword colour_start:  The starting colour of the linear gradient.
    @type colour_start:     str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end:    The ending colour of the linear gradient.
    @type colour_end:       str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:   The colour list to search for the colour names.  Can be either 'molmol' or 'x11'.
    @type colour_list:      str or None
    @return:                The list of Molmol commands.
    @rtype:                 list of str
    """

    # Specific Molmol macro creation function.
    macro = get_specific_fn('molmol_macro', cdp.pipe_type)

    # Get the macro.
    commands = macro(data_type, style, colour_start, colour_end, colour_list)

    # Return the macro commands.
    return commands


def macro_apply(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Execute a Molmol macro.

    @keyword data_type:     The data type to map to the structure.
    @type data_type:        str
    @keyword style:         The style of the macro.
    @type style:            str
    @keyword colour_start:  The starting colour of the linear gradient.
    @type colour_start:     str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end:    The ending colour of the linear gradient.
    @type colour_end:       str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:   The colour list to search for the colour names.  Can be either 'molmol' or 'x11'.
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
        molmol_obj.exec_cmd(command)


def macro_write(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir=None, force=False):
    """Create a Molmol macro.

    @keyword data_type:     The data type to map to the structure.
    @type data_type:        str
    @keyword style:         The style of the macro.
    @type style:            str
    @keyword colour_start:  The starting colour of the linear gradient.
    @type colour_start:     str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end:    The ending colour of the linear gradient.
    @type colour_end:       str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:   The colour list to search for the colour names.  Can be either 'molmol' or 'x11'.
    @type colour_list:      str or None
    @keyword file:          The name of the macro file to create.
    @type file:             str
    @keyword dir:           The name of the directory to place the macro file into.
    @type dir:              str
    @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
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
    file_path = get_file_path(file, dir)
    file = open_write_file(file, dir, force)

    # Loop over the commands and write them.
    for command in commands:
        file.write(command + "\n")

    # Close the file.
    file.close()

    # Add the file to the results file list.
    if not hasattr(cdp, 'result_files'):
        cdp.result_files = []
    cdp.result_files.append(['grace', 'Grace', file_path])
    status.observers.result_file.notify()


def ribbon():
    """Apply the Molmol ribbon style."""

    # Calculate the protons.
    molmol_obj.exec_cmd("CalcAtom 'H'")
    molmol_obj.exec_cmd("CalcAtom 'HN'")

    # Calculate the secondary structure.
    molmol_obj.exec_cmd("CalcSecondary")

    # Execute the ribbon macro.
    molmol_obj.exec_cmd("XMacStand ribbon.mac")


def tensor_pdb(file=None):
    """Display the diffusion tensor geometric structure.

    @keyword file:  The name of the PDB file containing the tensor geometric object.
    @type file:     str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # To overlay the structure with the diffusion tensor, select all and reorient to the PDB frame.
    molmol_obj.exec_cmd("SelectAtom ''")
    molmol_obj.exec_cmd("SelectBond ''")
    molmol_obj.exec_cmd("SelectAngle ''")
    molmol_obj.exec_cmd("SelectDist ''")
    molmol_obj.exec_cmd("SelectPrim ''")
    molmol_obj.exec_cmd("RotateInit")
    molmol_obj.exec_cmd("MoveInit")

    # Read in the tensor PDB file and force Molmol to recognise the CONECT records (not that it will show the bonds)!
    molmol_obj.exec_cmd("ReadPdb " + file)
    file_parts = split(file, '.')
    molmol_obj.exec_cmd("SelectMol '@" + file_parts[0] + "'")
    molmol_obj.exec_cmd("CalcBond 1 1 1")

    # Apply the 'ball/stick' style to the tensor.
    molmol_obj.exec_cmd("SelectAtom '0'")
    molmol_obj.exec_cmd("SelectBond '0'")
    molmol_obj.exec_cmd("SelectAtom ':TNS'")
    molmol_obj.exec_cmd("SelectBond ':TNS'")
    molmol_obj.exec_cmd("XMacStand ball_stick.mac")

    # Touch up.
    molmol_obj.exec_cmd("RadiusAtom 1")
    molmol_obj.exec_cmd("SelectAtom ':TNS@C*'")
    molmol_obj.exec_cmd("RadiusAtom 1.5")


def view():
    """Start Molmol."""

    # Open a Molmol pipe.
    if molmol_obj.running():
        raise RelaxError("The Molmol pipe already exists.")
    else:
        molmol_obj.open_gui()
