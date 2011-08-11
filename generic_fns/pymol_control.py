###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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

# Dependency check module.
import dep_check

# Python module imports.
if dep_check.pymol_module:
    import pymol
from math import pi
from numpy import float64, transpose, zeros
from os import sep
from subprocess import PIPE, Popen

# relax module imports.
from generic_fns.mol_res_spin import exists_mol_res_spin_data
from generic_fns import pipes
from maths_fns.rotation_matrix import euler_to_R_zyz, R_to_axis_angle
from relax_errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError
from relax_io import file_root, get_file_path, open_write_file, test_binary
from specific_fns.setup import get_specific_fn
from status import Status; status = Status()


class Pymol:
    """The PyMOL execution object."""

    def __init__(self, exec_mode=None):
        """Set up the PyMOL execution object.

        @keyword exec_mode: The execution mode which can be either 'module' or 'external'.
        @type exec_mode:    None or str
        """

        # Variable for storing the pymol command history.
        self.command_history = ""

        # The pymol mode of operation.
        self.exec_mode = exec_mode
        if not exec_mode:
            if dep_check.pymol_module:
                self.exec_mode = 'module'
                self.open = False
            else:
                self.exec_mode = 'external'


    def clear_history(self):
        """Clear the PyMOL command history."""

        self.command_history = ""


    def exec_cmd(self, command=None, store_command=True):
        """Execute a PyMOL command.

        @param command:         The PyMOL command to send into the program.
        @type command:          str
        @param store_command:   A flag specifying if the command should be stored in the history
                                variable.
        @type store_command:    bool
        """

        # Reopen the GUI if needed.
        if not self.running():
            self.open_gui()

        # Execute the command.
        if self.exec_mode == 'module':
            pymol.cmd.do(command)
        else:
            self.pymol.write(command + '\n')

        # Place the command in the command history.
        if store_command:
            self.command_history = self.command_history + command + "\n"


    def open_gui(self):
        """Open the PyMOL GUI."""

        # Use the PyMOL python modules.
        if self.exec_mode == 'module':
            # Open the GUI.
            pymol.finish_launching()
            self.open = True

        # Otherwise execute PyMOL on the command line.
        if self.exec_mode == 'external':
            # Test that the PyMOL binary exists.
            test_binary('pymol')

            # Open PyMOL as a pipe.
            self.pymol = Popen(['pymol', '-qpK'], stdin=PIPE).stdin

        # Execute the command history.
        if len(self.command_history) > 0:
            self.exec_cmd(self.command_history, store_command=0)
            return

        # Test if the PDB file has been loaded.
        if hasattr(cdp, 'structure'):
            self.open_pdb()


    def open_pdb(self):
        """Open the PDB file in PyMOL."""

        # Test if PyMOL is running.
        if not self.running():
            return

        # Reinitialise PyMOL.
        self.exec_cmd("reinitialize")

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
                self.exec_cmd("load " + file)

                # Add to the open file list.
                open_files.append(file)


    def running(self):
        """Test if PyMOL is running.

        @return:    Whether the Molmol pipe is open or not.
        @rtype:     bool
        """

        # Test if PyMOL module interface is already running.
        if self.exec_mode == 'module':
            return self.open

        # Test if command line PyMOL is already running.
        if self.exec_mode == 'external':
            # Pipe exists.
            if not hasattr(self, 'pymol'):
                return False

            # Test if the pipe has been broken.
            try:
                self.pymol.write('\n')
            except IOError:
                return False

            # PyMOL is running.
            return True



# Initialise the Pymol executable object.
pymol_obj = Pymol('external')
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
            pymol_obj.exec_cmd("cmd.hide('everything'," + repr(id) + ")")

            # Show the cartoon style.
            pymol_obj.exec_cmd("cmd.show('cartoon'," + repr(id) + ")")

            # Colour by secondary structure.
            pymol_obj.exec_cmd("util.cbss(" + repr(id) + ", 'red', 'yellow', 'green')")


def command(command):
    """Function for sending PyMOL commands to the program pipe.

    @param command: The command to send into the program.
    @type command:  str
    """

    # Pass the command to PyMOL.
    pymol_obj.exec_cmd(command)


def cone_pdb(file=None):
    """Display the cone geometric object.

    @keyword file:  The name of the file containing the cone geometric object.
    @type file:     str
    """

    # Read in the cone PDB file.
    pymol_obj.exec_cmd("load " + file)


    # The cone axes.
    ################

    # Select the AVE, XAX, YAX, ZAX, and SIM residues.
    pymol_obj.exec_cmd("select (resn AVE,XAX,YAX,ZAX,SIM)")

    # Show the vector as a stick.
    pymol_obj.exec_cmd("show stick, 'sele'")

    # Colour it blue.
    pymol_obj.exec_cmd("color cyan, 'sele'")

    # Select the atom used for labelling.
    pymol_obj.exec_cmd("select (resn AVE,XAX,YAX,ZAX,SIM and symbol N)")

    # Hide the atom.
    pymol_obj.exec_cmd("hide ('sele')")

    # Label using the atom name.
    pymol_obj.exec_cmd("cmd.label(\"sele\",\"name\")")


    # The cone object.
    ##################

    # Select the CON residue.
    pymol_obj.exec_cmd("select (resn CON,EDG)")

    # Hide everything.
    pymol_obj.exec_cmd("hide ('sele')")

    # Show as 'sticks'.
    pymol_obj.exec_cmd("show sticks, 'sele'")

    # Colour it white.
    pymol_obj.exec_cmd("color white, 'sele'")

    # Shorten the stick width from 0.25 to 0.15.
    pymol_obj.exec_cmd("set stick_radius,0.15000")

    # Set a bit of transparency.
    pymol_obj.exec_cmd("set stick_transparency, 0.3")


    # Clean up.
    ###########

    # Remove the selection.
    pymol_obj.exec_cmd("cmd.delete('sele')")


    # Rotate to the average position.
    #################################

    # The average position rotation.
    ave_pos_R = zeros((3, 3), float64)
    euler_to_R_zyz(cdp.ave_pos_alpha, cdp.ave_pos_beta, cdp.ave_pos_gamma, ave_pos_R)

    # The rotation is passive (need to rotated the moving domain back into the average position defined in the non-moving domain PDB frame).
    R = transpose(ave_pos_R)

    # Convert to axis-angle notation.
    axis, angle = R_to_axis_angle(R)

    # The PDB file to rotate.
    for i in range(len(cdp.domain_to_pdb)):
        if cdp.domain_to_pdb[i][0] != cdp.ref_domain:
            pdb = cdp.domain_to_pdb[i][1]

    # Execute the pymol command to rotate.
    pymol_obj.exec_cmd("cmd.rotate([%s, %s, %s], %s, '%s', origin=[%s, %s, %s])" % (axis[0], axis[1], axis[2], angle/pi*180.0, pdb, cdp.pivot[0], cdp.pivot[1], cdp.pivot[2]))


def create_macro(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Create an array of PyMOL commands.

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
    @return:                The list of PyMOL commands.
    @rtype:                 list of str
    """

    # Specific PyMOL macro creation function.
    macro = get_specific_fn('pymol_macro', cdp.pipe_type)

    # Get the macro.
    commands = macro(data_type, style, colour_start, colour_end, colour_list)

    # Return the macro commands.
    return commands


def macro_exec(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Execute a PyMOL macro.

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
        pymol_obj.exec_cmd(command)


def tensor_pdb(file=None):
    """Display the diffusion tensor geometric structure.

    @keyword file:  The name of the file containing the diffusion tensor geometric object.
    @type file:     str
    """

    # Test if the current data pipe exists.
    pipes.test()

    # Read in the tensor PDB file.
    pymol_obj.exec_cmd("load " + file)


    # The tensor object.
    ####################

    # Select the TNS residue.
    pymol_obj.exec_cmd("select resn TNS")

    # Hide everything.
    pymol_obj.exec_cmd("hide ('sele')")

    # Show as 'sticks'.
    pymol_obj.exec_cmd("show sticks, 'sele'")


    # Centre of mass.
    #################

    # Select the COM residue.
    pymol_obj.exec_cmd("select resn COM")

    # Show the centre of mass as the dots representation.
    pymol_obj.exec_cmd("show dots, 'sele'")

    # Colour it blue.
    pymol_obj.exec_cmd("color blue, 'sele'")


    # The diffusion tensor axes.
    ############################

    # Select the AXS residue.
    pymol_obj.exec_cmd("select resn AXS")

    # Hide everything.
    pymol_obj.exec_cmd("hide ('sele')")

    # Show as 'sticks'.
    pymol_obj.exec_cmd("show sticks, 'sele'")

    # Colour it cyan.
    pymol_obj.exec_cmd("color cyan, 'sele'")

    # Select the N atoms of the AXS residue (used to display the axis labels).
    pymol_obj.exec_cmd("select (resn AXS and elem N)")

    # Label the atoms.
    pymol_obj.exec_cmd("label 'sele', name")



    # Monte Carlo simulations.
    ##########################

    # Select the SIM residue.
    pymol_obj.exec_cmd("select resn SIM")

    # Colour it.
    pymol_obj.exec_cmd("colour cyan, 'sele'")


    # Clean up.
    ###########

    # Remove the selection.
    pymol_obj.exec_cmd("cmd.delete('sele')")


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
    pymol_obj.exec_cmd("load " + file)


    # Create a surface.
    ###################

    # Select the vector distribution.
    pymol_obj.exec_cmd("cmd.show('surface', " + repr(id) + ")")


def view():
    """Start PyMOL."""

    # Open PyMOL.
    if pymol_obj.running():
        raise RelaxError("PyMOL is already running.")
    else:
        pymol_obj.open_gui()


def write(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir=None, force=False):
    """Create a PyMOL macro file.

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
