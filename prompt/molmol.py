###############################################################################
#                                                                             #
# Copyright (C) 2003-2011 Edward d'Auvergne                                   #
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
"""Module containing the 'molmol' user function class for interacting with MOLMOL."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class, _build_doc
import arg_check
import colour
from generic_fns import molmol
from specific_fns.model_free.molmol import Molmol


class Molmol(User_fn_class):
    """Class for interfacing with Molmol."""

    def clear_history(self):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molmol.clear_history()"
            print(text)

        # Execute the functional code.
        molmol.clear_history()

    # The function doc info.
    clear_history._doc_title = "Clear the Molmol command history."
    clear_history._doc_title_short = "Clear Molmol history."""
    clear_history._doc_desc = """
        This will clear the Molmol history from memory.
        """
    _build_doc(clear_history)


    def command(self, command=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molmol.command("
            text = text + "command=" + repr(command) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(command, 'MOLMOL command')

        # Execute the functional code.
        molmol.command(command=command)

    # The function doc info.
    command._doc_title = "Execute a user supplied Molmol command."
    command._doc_title_short = "Molmol command execution."
    command._doc_args = [
        ["command", "The Molmol command to execute."]
    ]
    command._doc_desc = """
        This allows Molmol commands to be passed to the program.  This can be useful for automation or scripting.
        """
    command._doc_examples = """
        To reinitialise the Molmol instance, type:

        relax> molmol.command("InitAll yes")
        """
    _build_doc(command)


    def macro_exec(self, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molmol.macro_exec("
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
        molmol.macro_exec(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)

    # The function doc info.
    macro_exec._doc_title = "Execute Molmol macros."
    macro_exec._doc_title_short = "Molmol macro execution."
    macro_exec._doc_args = [
        ["data_type", "The data type to map to the structure."],
        ["style", "The style of the macro."],
        ["colour_start", "The starting colour, either an array or string, of the linear colour gradient."],
        ["colour_end", "The ending colour, either an array or string, of the linear colour gradient."],
        ["colour_list", "The list of colours to match the start and end strings."]
    ]
    macro_exec._doc_desc = """
        This allows spin specific values to be mapped to a structure through Molmol macros.  Currently only the 'classic' style, which is described below, is available.
        """
    macro_exec._doc_examples = """
        To map the order parameter values, S2, onto the structure using the classic style, type:

        relax> molmol.macro_exec('S2')
        relax> molmol.macro_exec(data_type='S2')
        relax> molmol.macro_exec(data_type='S2', style="classic")
        """
    macro_exec._doc_additional = [
        colour._linear_gradient_doc,
        Molmol._molmol_classic_style_doc,
        colour.__molmol_colours_prompt_doc__,
        colour.__x11_colours_prompt_doc__
    ]
    _build_doc(macro_exec)


    def ribbon(self):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molmol.ribbon()"
            print(text)

        # Execute the functional code.
        molmol.ribbon()

    # The function doc info.
    ribbon._doc_title = "Apply the Molmol ribbon style."
    ribbon._doc_title_short = "Molmol ribbon style application."
    ribbon._doc_desc = """
        This applies the Molmol ribbon style which is equivalent to clicking on 'ribbon' in the Molmol side menu.  To do this, the following commands are executed:

            CalcAtom 'H'
            CalcAtom 'HN'
            CalcSecondary
            XMacStand ribbon.mac
        """
    ribbon._doc_examples = """
        To apply the ribbon style to the PDB file loaded, type:

        relax> molmol.ribbon()
        """
    _build_doc(ribbon)


    def tensor_pdb(self, file=None):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molmol.tensor_pdb("
            text = text + "file=" + repr(file) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str_or_inst(file, 'file name')

        # Execute the functional code.
        molmol.tensor_pdb(file=file)

    # The function doc info.
    tensor_pdb._doc_title = "Display the diffusion tensor PDB geometric object over the loaded PDB."
    tensor_pdb._doc_title_short = "Diffusion tensor and structure display."
    tensor_pdb._doc_args = [
        ["file", "The name of the PDB file containing the tensor geometric object."]
    ]
    tensor_pdb._doc_desc = """
        In executing this user function, a PDB file must have previously been loaded , a geometric object or polygon representing the Brownian rotational diffusion tensor will be overlain with the loaded PDB file and displayed within Molmol.  The PDB file containing the geometric object must be created using the complementary structure.create_diff_tensor_pdb user function.

        To display the diffusion tensor, the multiple commands will be executed.  To overlay the structure with the diffusion tensor, everything will be selected and reoriented and moved to their original PDB frame positions:

            SelectAtom ''
            SelectBond ''
            SelectAngle ''
            SelectDist ''
            SelectPrim ''
            RotateInit
            MoveInit

        Next the tensor PDB file is read in, selected, and the covalent bonds of the PDB CONECT records calculated:

            ReadPdb file
            SelectMol '@file'
            CalcBond 1 1 1

        Then only the atoms and bonds of the geometric object are selected and the 'ball/stick' style applied:

            SelectAtom '0'
            SelectBond '0'
            SelectAtom ':TNS'
            SelectBond ':TNS'
            XMacStand ball_stick.mac

        The appearance is finally touched up:

            RadiusAtom 1
            SelectAtom ':TNS@C*'
            RadiusAtom 1.5
        """
    _build_doc(tensor_pdb)


    def view(self):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molmol.view()"
            print(text)

        # Execute the functional code.
        molmol.view()

    # The function doc info.
    view._doc_title = "View the collection of molecules from the loaded PDB file."
    view._doc_title_short = "Molecule viewing."
    view._doc_desc = """
        This will simply launch Molmol.
        """
    view._doc_examples = """
        relax> molmol.view()
        """
    _build_doc(view)


    def write(self, data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None, file=None, dir='molmol', force=False):
        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "molmol.write("
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
        molmol.write(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, file=file, dir=dir, force=force)

    # The function doc info.
    write._doc_title = "Create Molmol macros."
    write._doc_title_short = "Molmol macro creation."
    write._doc_args = [
        ["data_type", "The data type to map to the structure."],
        ["style", "The style of the macro."],
        ["colour_start", "The starting colour, either an array or string, of the linear colour gradient."],
        ["colour_end", "The ending colour, either an array or string, of the linear colour gradient."],
        ["colour_list", "The list of colours to match the start and end strings."],
        ["file", "The name of the file."],
        ["dir", "The directory name."],
        ["force", "A flag which, if set to True, will cause the file to be overwritten."]
    ]
    write._doc_desc = """
        This allows residues specific values to be mapped to a structure through the creation of a Molmol '*.mac' macro which can be executed in Molmol by clicking on 'File, Macro, Execute User...'.  Currently only the 'classic' style, which is described below, is available.
        """
    write._doc_examples = """
        To create a Molmol macro mapping the order parameter values, S2, onto the structure using
        the classic style, type:

        relax> molmol.write('S2')
        relax> molmol.write(data_type='S2')
        relax> molmol.write(data_type='S2', style="classic", file='s2.mac', dir='molmol')
        """
    write._doc_additional = [
        colour._linear_gradient_doc,
        Molmol._molmol_classic_style_doc,
        colour.__molmol_colours_prompt_doc__,
        colour.__x11_colours_prompt_doc__
    ]
    _build_doc(write)
