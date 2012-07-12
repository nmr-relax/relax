###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""The molmol user function definitions for interacting with Molmol."""

# Python module imports.
from os import sep
import wx

# relax module imports.
import colour
from generic_fns import molmol
from graphics import WIZARD_IMAGE_PATH
from specific_fns.model_free.molmol import Molmol
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('molmol')
uf_class.title = "Class for interfacing with Molmol."
uf_class.menu_text = "&molmol"
uf_class.gui_icon = "relax.molmol"


# The molmol.clear_history user function.
uf = uf_info.add_uf('molmol.clear_history')
uf.title = "Clear the Molmol command history."
uf.title_short = "Clear Molmol history."""
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will clear the Molmol history from memory.")
uf.backend = molmol.molmol_obj.clear_history
uf.menu_text = "clear_&history"
uf.wizard_size = (600, 300)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'


# The molmol.command user function.
uf = uf_info.add_uf('molmol.command')
uf.title = "Execute a user supplied Molmol command."
uf.title_short = "Molmol command execution."
uf.add_keyarg(
    name = "command",
    py_type = "str",
    desc_short = "Molmol command",
    desc = "The Molmol command to execute."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows Molmol commands to be passed to the program.  This can be useful for automation or scripting.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To reinitialise the Molmol instance, type:")
uf.desc[-1].add_prompt("relax> molmol.command(\"InitAll yes\")")
uf.backend = molmol.command
uf.menu_text = "&command"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'


# The molmol.macro_apply user function.
uf = uf_info.add_uf('molmol.macro_apply')
uf.title = "Execute Molmol macros."
uf.title_short = "Molmol macro execution."
uf.display = True
uf.add_keyarg(
    name = "data_type",
    py_type = "str",
    desc_short = "data type",
    desc = "The data type to map to the structure."
)
uf.add_keyarg(
    name = "style",
    default = "classic",
    py_type = "str",
    desc_short = "style",
    desc = "The style of the macro.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["classic"],
    wiz_read_only = True
)
uf.add_keyarg(
    name = "colour_start_name",
    py_type = "str",
    desc_short = "starting colour (by name)",
    desc = "The name of the starting colour of the linear colour gradient.  This can be either one of the X11 or one of the Molmol colour names listed in the description.  If this is set, then the starting colour RGB colour array cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_start_rgb",
    py_type = "num_list",
    dim = 3,
    desc_short = "starting colour (RGB colour array)",
    desc = "The starting colour of the linear colour gradient.  This is an RGB colour array with values ranging from 0 to 1.  If this is set, then the starting colour name cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_end_name",
    py_type = "str",
    desc_short = "ending colour (by name)",
    desc = "The name of the ending colour of the linear colour gradient.  This can be either one of the X11 or one of the Molmol colour names listed in the description.  If this is set, then the ending colour RGB colour array cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_end_rgb",
    py_type = "num_list",
    dim = 3,
    desc_short = "ending colour (RGB colour array)",
    desc = "The ending colour of the linear colour gradient.  This is an RGB colour array with values ranging from 0 to 1.  If this is set, then the ending colour name cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_list",
    py_type = "str",
    desc_short = "colour list",
    desc = "The colour list to search for the colour names.  This can be either 'molmol' or 'x11'.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["molmol", "x11"],
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows spin specific values to be mapped to a structure through Molmol macros.  Currently only the 'classic' style, which is described below, is available.")
uf.desc.append(colour._linear_gradient_doc)
uf.desc.append(Molmol.classic_style_doc)
uf.desc.append(colour.__molmol_colours_doc__)
uf.desc.append(colour.__x11_colours_doc__)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To map the order parameter values, S2, onto the structure using the classic style, type:")
uf.desc[-1].add_prompt("relax> molmol.macro_apply('s2')")
uf.desc[-1].add_prompt("relax> molmol.macro_apply(data_type='s2')")
uf.desc[-1].add_prompt("relax> molmol.macro_apply(data_type='s2', style=\"classic\")")
uf.backend = molmol.macro_apply
uf.menu_text = "&macro_apply"
uf.gui_icon = "relax.molmol"
uf.wizard_size = (1000, 750)
uf.wizard_height_desc = 400
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'


# The molmol.macro_run user function.
uf = uf_info.add_uf('molmol.macro_run')
uf.title = "Open and execute the Molmol macro file."
uf.title_short = "Molmol macro file execution."
uf.display = True
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "",
    desc = "The name of the Molmol macro file.",
    wiz_filesel_wildcard = "Molmol macro files (*.mac)|*.mac;*.MAC",
    wiz_filesel_style = wx.FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    default = "molmol",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function is for opening and running a Molmol macro located within a text file.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To execute the macro file 's2.mac' located in the directory 'molmol', type:")
uf.desc[-1].add_prompt("relax> molmol.macro_run(file='s2.mac')")
uf.desc[-1].add_prompt("relax> molmol.macro_run(file='s2.mac', dir='molmol')")
uf.backend = molmol.macro_run
uf.menu_text = "macro_&run"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'


# The molmol.macro_write user function.
uf = uf_info.add_uf('molmol.macro_write')
uf.title = "Create Molmol macros."
uf.title_short = "Molmol macro creation."
uf.add_keyarg(
    name = "data_type",
    py_type = "str",
    desc_short = "data type",
    desc = "The data type to map to the structure."
)
uf.add_keyarg(
    name = "style",
    default = "classic",
    py_type = "str",
    desc_short = "style",
    desc = "The style of the macro.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["classic"],
    wiz_read_only = True,
)
uf.add_keyarg(
    name = "colour_start_name",
    py_type = "str",
    desc_short = "starting colour (by name)",
    desc = "The name of the starting colour of the linear colour gradient.  This can be either one of the X11 or one of the Molmol colour names listed in the description.  If this is set, then the starting colour RGB colour array cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_start_rgb",
    py_type = "num_list",
    dim = 3,
    desc_short = "starting colour (RGB colour array)",
    desc = "The starting colour of the linear colour gradient.  This is an RGB colour array with values ranging from 0 to 1.  If this is set, then the starting colour name cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_end_name",
    py_type = "str",
    desc_short = "ending colour (by name)",
    desc = "The name of the ending colour of the linear colour gradient.  This can be either one of the X11 or one of the Molmol colour names listed in the description.  If this is set, then the ending colour RGB colour array cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_end_rgb",
    py_type = "num_list",
    dim = 3,
    desc_short = "ending colour (RGB colour array)",
    desc = "The ending colour of the linear colour gradient.  This is an RGB colour array with values ranging from 0 to 1.  If this is set, then the ending colour name cannot be given.",
    can_be_none = True
)
uf.add_keyarg(
    name = "colour_list",
    py_type = "str",
    desc_short = "colour list",
    desc = "The colour list to search for the colour names.  This can be either 'molmol' or 'x11'.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["molmol", "x11"],
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The optional name of the file.",
    wiz_filesel_wildcard = "Molmol macro files (*.mac)|*.mac;*.MAC",
    wiz_filesel_style = wx.FD_SAVE,
    can_be_none = True
)
uf.add_keyarg(
    name = "dir",
    default = "molmol",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The optional directory to save the file to.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which, if set to True, will cause the file to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows residues specific values to be mapped to a structure through the creation of a Molmol '*.mac' macro which can be executed in Molmol by clicking on 'File, Macro, Execute User...'.  Currently only the 'classic' style, which is described below, is available.")
uf.desc.append(colour._linear_gradient_doc)
uf.desc.append(Molmol.classic_style_doc)
uf.desc.append(colour.__molmol_colours_doc__)
uf.desc.append(colour.__x11_colours_doc__)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To create a Molmol macro mapping the order parameter values, S2, onto the structure using the classic style, type:")
uf.desc[-1].add_prompt("relax> molmol.macro_write('s2')")
uf.desc[-1].add_prompt("relax> molmol.macro_write(data_type='s2')")
uf.desc[-1].add_prompt("relax> molmol.macro_write(data_type='s2', style=\"classic\", file='s2.mac', dir='molmol')")
uf.backend = molmol.macro_write
uf.menu_text = "macro_&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_size = (1000, 750)
uf.wizard_height_desc = 350
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'


# The molmol.ribbon user function.
uf = uf_info.add_uf('molmol.ribbon')
uf.title = "Apply the Molmol ribbon style."
uf.title_short = "Molmol ribbon style application."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This applies the Molmol ribbon style which is equivalent to clicking on 'ribbon' in the Molmol side menu.  To do this, the following commands are executed:")
uf.desc[-1].add_list_element("CalcAtom 'H'")
uf.desc[-1].add_list_element("CalcAtom 'HN'")
uf.desc[-1].add_list_element("CalcSecondary")
uf.desc[-1].add_list_element("XMacStand ribbon.mac")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To apply the ribbon style to the PDB file loaded, type:")
uf.desc[-1].add_prompt("relax> molmol.ribbon()")
uf.backend = molmol.ribbon
uf.menu_text = "ri&bbon"
uf.wizard_size = (700, 500)
uf.wizard_height_desc = 450
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'


# The molmol.tensor_pdb user function.
uf = uf_info.add_uf('molmol.tensor_pdb')
uf.title = "Display the diffusion tensor PDB geometric object over the loaded PDB."
uf.title_short = "Diffusion tensor and structure display."
uf.add_keyarg(
    name = "file",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file containing the tensor geometric object.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = wx.FD_OPEN
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("In executing this user function, a PDB file must have previously been loaded , a geometric object or polygon representing the Brownian rotational diffusion tensor will be overlain with the loaded PDB file and displayed within Molmol.  The PDB file containing the geometric object must be created using the complementary structure.create_diff_tensor_pdb user function.")
uf.desc[-1].add_paragraph("To display the diffusion tensor, the multiple commands will be executed.  To overlay the structure with the diffusion tensor, everything will be selected and reoriented and moved to their original PDB frame positions:")
uf.desc[-1].add_list_element("SelectAtom ''")
uf.desc[-1].add_list_element("SelectBond ''")
uf.desc[-1].add_list_element("SelectAngle ''")
uf.desc[-1].add_list_element("SelectDist ''")
uf.desc[-1].add_list_element("SelectPrim ''")
uf.desc[-1].add_list_element("RotateInit")
uf.desc[-1].add_list_element("MoveInit")
uf.desc[-1].add_paragraph("Next the tensor PDB file is read in, selected, and the covalent bonds of the PDB CONECT records calculated:")
uf.desc[-1].add_list_element("ReadPdb file")
uf.desc[-1].add_list_element("SelectMol '@file'")
uf.desc[-1].add_list_element("CalcBond 1 1 1")
uf.desc[-1].add_paragraph("Then only the atoms and bonds of the geometric object are selected and the 'ball/stick' style applied:")
uf.desc[-1].add_list_element("SelectAtom '0'")
uf.desc[-1].add_list_element("SelectBond '0'")
uf.desc[-1].add_list_element("SelectAtom ':TNS'")
uf.desc[-1].add_list_element("SelectBond ':TNS'")
uf.desc[-1].add_list_element("XMacStand ball_stick.mac")
uf.desc[-1].add_paragraph("The appearance is finally touched up:")
uf.desc[-1].add_list_element("RadiusAtom 1")
uf.desc[-1].add_list_element("SelectAtom ':TNS@C*'")
uf.desc[-1].add_list_element("RadiusAtom 1.5")
uf.backend = molmol.tensor_pdb
uf.menu_text = "&tensor_pdb"
uf.wizard_height_desc = 550
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'


# The molmol.view user function.
uf = uf_info.add_uf('molmol.view')
uf.title = "View the collection of molecules from the loaded PDB file."
uf.title_short = "Molecule viewing."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will simply launch Molmol.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_prompt("relax> molmol.view()")
uf.backend = molmol.view
uf.menu_text = "&view"
uf.wizard_size = (600, 300)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
