###############################################################################
#                                                                             #
# Copyright (C) 2003-2013 Edward d'Auvergne                                   #
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
"""The pymol user function definitions for interacting with PyMOL."""

# Python module imports.
from os import sep
import dep_check
if dep_check.wx_module:
    from wx import FD_OPEN, FD_SAVE
else:
    FD_OPEN = -1
    FD_SAVE = -1

# relax module imports.
import colour
from graphics import WIZARD_IMAGE_PATH
from pipe_control import pymol_control
from specific_analyses.model_free.pymol import Pymol
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('pymol')
uf_class.title = "Class for interfacing with PyMOL."
uf_class.menu_text = "&pymol"
uf_class.gui_icon = "relax.pymol_icon"


# The pymol.cartoon user function.
uf = uf_info.add_uf('pymol.cartoon')
uf.title = "Apply the PyMOL cartoon style and colour by secondary structure."
uf.title_short = "PyMOL cartoon style application."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This applies the PyMOL cartoon style which is equivalent to hiding everything and clicking on show cartoon.  It also colours the cartoon with red helices, yellow strands, and green loops.  The following commands are executed:")
uf.desc[-1].add_list_element("cmd.hide('everything', file)")
uf.desc[-1].add_list_element("cmd.show('cartoon', file)")
uf.desc[-1].add_list_element("util.cbss(file, 'red', 'yellow', 'green')")
uf.desc[-1].add_paragraph("where file is the file name without the '.pdb' extension.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To apply this user function, type:")
uf.desc[-1].add_prompt("relax> pymol.cartoon()")
uf.backend = pymol_control.cartoon
uf.menu_text = "cart&oon"
uf.wizard_size = (700, 500)
uf.wizard_height_desc = 450
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.clear_history user function.
uf = uf_info.add_uf('pymol.clear_history')
uf.title = "Clear the PyMOL command history."""
uf.title_short = "Clear PyMOL history."""
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will clear the Pymol history from memory.")
uf.backend = pymol_control.pymol_obj.clear_history
uf.menu_text = "clear_&history"
uf.wizard_size = (600, 350)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.command user function.
uf = uf_info.add_uf('pymol.command')
uf.title = "Execute a user supplied PyMOL command."
uf.title_short = "PyMOL command execution."
uf.add_keyarg(
    name = "command",
    py_type = "str",
    desc_short = "PyMOL command",
    desc = "The PyMOL command to execute."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows PyMOL commands to be passed to the program.  This can be useful for automation or scripting.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To reinitialise the PyMOL instance, type:")
uf.desc[-1].add_prompt("relax> pymol.command(\"reinitialise\")")
uf.backend = pymol_control.command
uf.menu_text = "&command"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.cone_pdb user function.
uf = uf_info.add_uf('pymol.cone_pdb')
uf.title = "Display the cone PDB geometric object."
uf.title_short = "Cone PDB geometric object display."
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file containing the cone geometric object.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = FD_OPEN
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The PDB file containing the geometric object must be created using the complementary frame_order.cone_pdb or n_state_model.cone_pdb user functions.")
uf.desc[-1].add_paragraph("The cone PDB file is read in using the command:")
uf.desc[-1].add_list_element("load file")
uf.desc[-1].add_paragraph("The average CoM-pivot point vector, the residue 'AVE' is displayed using the commands:")
uf.desc[-1].add_list_element("select resn AVE")
uf.desc[-1].add_list_element("show sticks, 'sele'")
uf.desc[-1].add_list_element("color blue, 'sele'")
uf.desc[-1].add_paragraph("The cone object, the residue 'CON', is displayed using the commands:")
uf.desc[-1].add_list_element("select resn CON")
uf.desc[-1].add_list_element("hide ('sele')")
uf.desc[-1].add_list_element("show sticks, 'sele'")
uf.desc[-1].add_list_element("color white, 'sele'")
uf.backend = pymol_control.cone_pdb
uf.menu_text = "cone_&pdb"
uf.wizard_height_desc = 500
uf.wizard_size = (900, 700)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.macro_apply user function.
uf = uf_info.add_uf('pymol.macro_apply')
uf.title = "Execute PyMOL macros."
uf.title_short = "PyMOL macro execution."
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
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows spin specific values to be mapped to a structure through PyMOL macros.  Currently only the 'classic' style, which is described below, is available.")
uf.desc.append(colour._linear_gradient_doc)
uf.desc.append(Pymol.classic_style_doc)
uf.desc.append(colour.__molmol_colours_doc__)
uf.desc.append(colour.__x11_colours_doc__)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To map the order parameter values, S2, onto the structure using the classic style, type:")
uf.desc[-1].add_prompt("relax> pymol.macro_apply('s2')")
uf.desc[-1].add_prompt("relax> pymol.macro_apply(data_type='s2')")
uf.desc[-1].add_prompt("relax> pymol.macro_apply(data_type='s2', style=\"classic\")")
uf.backend = pymol_control.macro_apply
uf.menu_text = "&macro_apply"
uf.gui_icon = "relax.pymol_icon"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.macro_run user function.
uf = uf_info.add_uf('pymol.macro_run')
uf.title = "Open and execute the PyMOL macro file."
uf.title_short = "PyMOL macro file execution."
uf.display = True
uf.add_keyarg(
    name = "file",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PyMOL macro file.",
    wiz_filesel_wildcard = "PyMOL macro files (*.pml)|*.pml;*.PML",
    wiz_filesel_style = FD_OPEN
)
uf.add_keyarg(
    name = "dir",
    default = "pymol",
    py_type = "str",
    arg_type = "dir",
    desc_short = "directory name",
    desc = "The directory name.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This user function is for opening and running a PyMOL macro located within a text file.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To execute the macro file 's2.pml' located in the directory 'pymol', type:")
uf.desc[-1].add_prompt("relax> pymol.macro_run(file='s2.pml')")
uf.desc[-1].add_prompt("relax> pymol.macro_run(file='s2.pml', dir='pymol')")
uf.backend = pymol_control.macro_run
uf.menu_text = "macro_&run"
uf.gui_icon = "oxygen.actions.document-open"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.macro_write user function.
uf = uf_info.add_uf('pymol.macro_write')
uf.title = "Create PyMOL macros."
uf.title_short = "PyMOL macro creation."
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
    wiz_filesel_wildcard = "PyMOL macro files (*.pml)|*.pml;*.PML",
    wiz_filesel_style = FD_SAVE,
    can_be_none = True
)
uf.add_keyarg(
    name = "dir",
    default = "pymol",
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
uf.desc[-1].add_paragraph("This allows residues specific values to be mapped to a structure through the creation of a PyMOL macro which can be executed in PyMOL by clicking on 'File, Macro, Execute User...'.  Currently only the 'classic' style, which is described below, is available.")
uf.desc.append(colour._linear_gradient_doc)
uf.desc.append(Pymol.classic_style_doc)
uf.desc.append(colour.__molmol_colours_doc__)
uf.desc.append(colour.__x11_colours_doc__)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To create a PyMOL macro mapping the order parameter values, S2, onto the structure using the classic style, type:")
uf.desc[-1].add_prompt("relax> pymol.macro_write('s2')")
uf.desc[-1].add_prompt("relax> pymol.macro_write(data_type='s2')")
uf.desc[-1].add_prompt("relax> pymol.macro_write(data_type='s2', style=\"classic\", file='s2.pml', dir='pymol')")
uf.backend = pymol_control.macro_write
uf.menu_text = "macro_&write"
uf.gui_icon = "oxygen.actions.document-save"
uf.wizard_height_desc = 330
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.tensor_pdb user function.
uf = uf_info.add_uf('pymol.tensor_pdb')
uf.title = "Display the diffusion tensor PDB geometric object over the loaded PDB."
uf.title_short = "Diffusion tensor and structure display."
uf.add_keyarg(
    name = "file",
    py_type = "str_or_inst",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file containing the tensor geometric object.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = FD_OPEN
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("In executing this user function, a PDB file must have previously been loaded into this data pipe a geometric object or polygon representing the Brownian rotational diffusion tensor will be overlain with the loaded PDB file and displayed within PyMOL.  The PDB file containing the geometric object must be created using the complementary structure.create_diff_tensor_pdb user function.")
uf.desc[-1].add_paragraph("The tensor PDB file is read in using the command:")
uf.desc[-1].add_list_element("load file")
uf.desc[-1].add_paragraph("The centre of mass residue 'COM' is displayed using the commands:")
uf.desc[-1].add_list_element("select resn COM")
uf.desc[-1].add_list_element("show dots, 'sele'")
uf.desc[-1].add_list_element("color blue, 'sele'")
uf.desc[-1].add_paragraph("The axes of the diffusion tensor, the residue 'AXS', is displayed using the commands:")
uf.desc[-1].add_list_element("select resn AXS")
uf.desc[-1].add_list_element("hide ('sele')")
uf.desc[-1].add_list_element("show sticks, 'sele'")
uf.desc[-1].add_list_element("color cyan, 'sele'")
uf.desc[-1].add_list_element("label 'sele', name")
uf.desc[-1].add_paragraph("The simulation axes, the residues 'SIM', are displayed using the commands:")
uf.desc[-1].add_list_element("select resn SIM")
uf.desc[-1].add_list_element("colour cyan, 'sele'")
uf.backend = pymol_control.tensor_pdb
uf.menu_text = "&tensor_pdb"
uf.wizard_height_desc = 550
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'


# The pymol.vector_dist user function.
uf = uf_info.add_uf('pymol.vector_dist')
uf.title = "Display the PDB file representation of the XH vector distribution."
uf.title_short = "XH vector distribution display."
uf.add_keyarg(
    name = "file",
    default = "XH_dist.pdb",
    py_type = "str",
    arg_type = "file sel",
    desc_short = "file name",
    desc = "The name of the PDB file containing the vector distribution.",
    wiz_filesel_wildcard = "PDB files (*.pdb)|*.pdb;*.PDB",
    wiz_filesel_style = FD_OPEN
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("A PDB file of the macromolecule must have previously been loaded as the vector distribution will be overlain with the macromolecule within PyMOL.  The PDB file containing the vector distribution must be created using the complementary structure.create_vector_dist user function.")
uf.desc[-1].add_paragraph("The vector distribution PDB file is read in using the command:")
uf.desc[-1].add_list_element("load file")
uf.backend = pymol_control.vector_dist
uf.menu_text = "vector_&dist"
uf.wizard_size = (800, 500)
uf.wizard_height_desc = 450
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'

# The pymol.view user function.
uf = uf_info.add_uf('pymol.view')
uf.title = "View the collection of molecules from the loaded PDB file."
uf.title_short = "Molecule viewing."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will simply launch Pymol.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_prompt("relax> pymol.view()")
uf.backend = pymol_control.view
uf.menu_text = "&view"
uf.wizard_size = (600, 350)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
