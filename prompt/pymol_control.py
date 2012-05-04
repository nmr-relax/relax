###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'pymol' user function class for interacting with PyMOL."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
import colour
from generic_fns import pymol_control
from specific_fns.model_free.pymol import Pymol
from status import Status; status = Status()


class Pymol(User_fn_class):
    """Class for interfacing with PyMOL."""

    def cartoon(self):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.cartoon()"
            print(text)

        # Execute the functional code.
        pymol_control.cartoon()

    # The function doc info.
    cartoon._doc_title = "Apply the PyMOL cartoon style and colour by secondary structure."
    cartoon._doc_title_short = "PyMOL cartoon style application."
    cartoon._doc_desc = """
        This applies the PyMOL cartoon style which is equivalent to hiding everything and clicking on show cartoon.  It also colours the cartoon with red helices, yellow strands, and green loops.  The following commands are executed:

            cmd.hide('everything', file)
            cmd.show('cartoon', file)
            util.cbss(file, 'red', 'yellow', 'green')

        where file is the file name without the '.pdb' extension.
        """
    cartoon._doc_examples = """
        To apply this user function, type:

        relax> pymol.cartoon()
        """
    _build_doc(cartoon)


    def clear_history(self):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.clear_history()"
            print(text)

        # Execute the functional code.
        pymol_control.clear_history()

    # The function doc info.
    clear_history._doc_title = "Clear the PyMOL command history."""
    clear_history._doc_title_short = "Clear PyMOL history."""
    clear_history._doc_desc = """
        This will clear the Pymol history from memory.
        """
    _build_doc(clear_history)


    def command(self, command=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.command("
            text = text + "command=" + repr(command) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(command, 'PyMOL command')

        # Execute the functional code.
        pymol_control.command(command=command)

    # The function doc info.
    command._doc_title = "Execute a user supplied PyMOL command."
    command._doc_title_short = "PyMOL command execution."
    command._doc_args = [
        ["command", "The PyMOL command to execute."]
    ]
    command._doc_desc = """
        This allows PyMOL commands to be passed to the program.  This can be useful for automation or scripting.
        """
    command._doc_examples = """
        To reinitialise the PyMOL instance, type:

        relax> pymol.command("reinitialise")
        """
    _build_doc(command)


    def cone_pdb(self, file=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.cone_pdb("
            text = text + "file=" + repr(file) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')

        # Execute the functional code.
        pymol_control.cone_pdb(file=file)

    # The function doc info.
    cone_pdb._doc_title = "Display the cone PDB geometric object."
    cone_pdb._doc_title_short = "Cone PDB geometric object display."
    cone_pdb._doc_args = [
        ["file", "The name of the PDB file containing the cone geometric object."]
    ]
    cone_pdb._doc_desc = """
        The PDB file containing the geometric object must be created using the complementary frame_order.cone_pdb or n_state_model.cone_pdb user functions.

        The cone PDB file is read in using the command:

            load file

        The average CoM-pivot point vector, the residue 'AVE' is displayed using the commands:

            select resn AVE
            show sticks, 'sele'
            color blue, 'sele'

        The cone object, the residue 'CON', is displayed using the commands:

            select resn CON
            hide ('sele')
            show sticks, 'sele'
            color white, 'sele'
        """
    _build_doc(cone_pdb)


    def macro_apply(self, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.macro_apply("
            text = text + "data_type=" + repr(data_type)
            text = text + ", style=" + repr(style)
            text = text + ", colour_start=" + repr(colour_start)
            text = text + ", colour_end=" + repr(colour_end)
            text = text + ", colour_list=" + repr(colour_list) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(data_type, 'data type')
        arg_check.is_str(style, 'style')
        arg_check.is_str_or_num_list(colour_start, 'starting colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str_or_num_list(colour_end, 'ending colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str(colour_list, 'colour list', can_be_none=True)

        # Execute the functional code.
        pymol_control.macro_apply(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)

    # The function doc info.
    macro_apply._doc_title = "Execute PyMOL macros."
    macro_apply._doc_title_short = "PyMOL macro execution."
    macro_apply._doc_args = [
        ["data_type", "The data type to map to the structure."],
        ["style", "The style of the macro."],
        ["colour_start", "The starting colour, either an array or string, of the linear colour gradient."],
        ["colour_end", "The ending colour, either an array or string, of the linear colour gradient."],
        ["colour_list", "The list of colours to match the start and end strings."]
    ]
    macro_apply._doc_desc = """
        This allows spin specific values to be mapped to a structure through PyMOL macros.  Currently only the 'classic' style, which is described below, is available.
        """
    macro_apply._doc_examples = """
        To map the order parameter values, S2, onto the structure using the classic style, type:

        relax> pymol.macro_apply('s2')
        relax> pymol.macro_apply(data_type='s2')
        relax> pymol.macro_apply(data_type='s2', style="classic")
        """
    macro_apply._doc_additional = [
        colour._linear_gradient_doc,
        Pymol.classic_style_doc,
        colour.__molmol_colours_prompt_doc__,
        colour.__x11_colours_prompt_doc__
    ]
    _build_doc(macro_apply)


    def macro_run(self, file=None, dir='pymol'):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.macro_run("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')
        arg_check.is_str(dir, 'directory name', can_be_none=True)

        # Execute the functional code.
        pymol_control.macro_run(file=file, dir=dir)

    # The function doc info.
    macro_run._doc_title = "Open and execute the PyMOL macro file."
    macro_run._doc_title_short = "PyMOL macro file execution."
    macro_run._doc_args = [
        ["file", "The name of the PyMOL macro file."],
        ["dir", "The directory name."],
    ]
    macro_run._doc_desc = """
        This user function is for opening and running a PyMOL macro located within a text file.
        """
    macro_run._doc_examples = """
        To execute the macro file 's2.pml' located in the directory 'pymol', type:

        relax> pymol.macro_run(file='s2.pml')
        relax> pymol.macro_run(file='s2.pml', dir='pymol')
        """
    _build_doc(macro_run)


    def macro_write(self, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir='pymol', force=False):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.macro_write("
            text = text + "data_type=" + repr(data_type)
            text = text + ", style=" + repr(style)
            text = text + ", colour_start=" + repr(colour_start)
            text = text + ", colour_end=" + repr(colour_end)
            text = text + ", colour_list=" + repr(colour_list)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(data_type, 'data type')
        arg_check.is_str(style, 'style')
        arg_check.is_str_or_num_list(colour_start, 'starting colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str_or_num_list(colour_end, 'ending colour of the linear gradient', size=3, can_be_none=True)
        arg_check.is_str(colour_list, 'colour list', can_be_none=True)
        arg_check.is_str_or_inst(file, 'file name', can_be_none=True)
        arg_check.is_str(dir, 'directory name', can_be_none=True)
        arg_check.is_bool(force, 'force flag')

        # Execute the functional code.
        pymol_control.macro_write(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, file=file, dir=dir, force=force)

    # The function doc info.
    macro_write._doc_title = "Create PyMOL macros."
    macro_write._doc_title_short = "PyMOL macro creation."
    macro_write._doc_args = [
        ["data_type", "The data type to map to the structure."],
        ["style", "The style of the macro."],
        ["colour_start", "The starting colour, either an array or string, of the linear colour gradient."],
        ["colour_end", "The ending colour, either an array or string, of the linear colour gradient."],
        ["colour_list", "The list of colours to match the start and end strings."],
        ["file", "The optional name of the file."],
        ["dir", "The optional directory to save the file to."],
        ["force", "A flag which, if set to True, will cause the file to be overwritten."]
    ]
    macro_write._doc_desc = """
        This allows residues specific values to be mapped to a structure through the creation of a PyMOL macro which can be executed in PyMOL by clicking on 'File, Macro, Execute User...'.  Currently only the 'classic' style, which is described below, is available.
        """
    macro_write._doc_examples = """
        To create a PyMOL macro mapping the order parameter values, S2, onto the structure using
        the classic style, type:

        relax> pymol.macro_write('s2')
        relax> pymol.macro_write(data_type='s2')
        relax> pymol.macro_write(data_type='s2', style="classic", file='s2.pml', dir='pymol')
        """
    macro_write._doc_additional = [
        colour._linear_gradient_doc,
        Pymol.classic_style_doc,
        colour.__molmol_colours_prompt_doc__,
        colour.__x11_colours_prompt_doc__
    ]
    _build_doc(macro_write)


    def tensor_pdb(self, file=None):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.tensor_pdb("
            text = text + "file=" + repr(file) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_inst(file, 'file name')

        # Execute the functional code.
        pymol_control.tensor_pdb(file=file)

    # The function doc info.
    tensor_pdb._doc_title = "Display the diffusion tensor PDB geometric object over the loaded PDB."
    tensor_pdb._doc_title_short = "Diffusion tensor and structure display."
    tensor_pdb._doc_args = [
        ["file", "The name of the PDB file containing the tensor geometric object."]
    ]
    tensor_pdb._doc_desc = """
        In executing this user function, a PDB file must have previously been loaded into this data pipe a geometric object or polygon representing the Brownian rotational diffusion tensor will be overlain with the loaded PDB file and displayed within PyMOL.  The PDB file containing the geometric object must be created using the complementary structure.create_diff_tensor_pdb user function.

        The tensor PDB file is read in using the command:

            load file

        The centre of mass residue 'COM' is displayed using the commands:

            select resn COM
            show dots, 'sele'
            color blue, 'sele'

        The axes of the diffusion tensor, the residue 'AXS', is displayed using the commands:

            select resn AXS
            hide ('sele')
            show sticks, 'sele'
            color cyan, 'sele'
            label 'sele', name

        The simulation axes, the residues 'SIM', are displayed using the commands:

            select resn SIM
            colour cyan, 'sele'
        """
    _build_doc(tensor_pdb)


    def vector_dist(self, file='XH_dist.pdb'):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.vector_dist("
            text = text + "file=" + repr(file) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(file, 'file name')

        # Execute the functional code.
        pymol_control.vector_dist(file=file)

    # The function doc info.
    vector_dist._doc_title = "Display the PDB file representation of the XH vector distribution."
    vector_dist._doc_title_short = "XH vector distribution display."
    vector_dist._doc_args = [
        ["file", "The name of the PDB file containing the vector distribution."]
    ]
    vector_dist._doc_desc = """
        A PDB file of the macromolecule must have previously been loaded as the vector distribution will be overlain with the macromolecule within PyMOL.  The PDB file containing the vector distribution must be created using the complementary structure.create_vector_dist user function.

        The vector distribution PDB file is read in using the command:

            load file
        """
    _build_doc(vector_dist)


    def view(self):
        # Function intro text.
        if status.prompt_intro:
            text = status.ps3 + "pymol.view()"
            print(text)

        # Execute the functional code.
        pymol_control.view()

    # The function doc info.
    view._doc_title = "View the collection of molecules from the loaded PDB file."
    view._doc_title_short = "Molecule viewing."
    view._doc_desc = """
        This will simply launch Pymol.
        """
    view._doc_examples = """
        relax> pymol.view()
        """
    _build_doc(view)
