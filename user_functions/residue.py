###############################################################################
#                                                                             #
# Copyright (C) 2007-2013 Edward d'Auvergne                                   #
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
"""The residue user function definitions."""

# relax module imports.
from pipe_control.mol_res_spin import copy_residue, create_residue, delete_residue, display_residue, get_molecule_names, get_residue_ids, id_string_doc, name_residue, number_residue
from pipe_control import pipes
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('residue')
uf_class.title = "Class for manipulating the residue data."
uf_class.menu_text = "&residue"
uf_class.gui_icon = "relax.residue"


# The residue.copy user function.
uf = uf_info.add_uf('residue.copy')
uf.title = "Copy all data associated with a residue."
uf.title_short = "Residue copying."
uf.display = True
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source pipe",
    desc = "The data pipe containing the residue from which the data will be copied.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "res_from",
    py_type = "str",
    desc_short = "source residue ID",
    desc = "The residue ID string of the residue to copy the data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination pipe",
    desc = "The data pipe to copy the data to.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "res_to",
    py_type = "str",
    desc_short = "destination residue ID",
    desc = "The residue ID string of the residue to copy the data to.  If left blank, the new residue will have the same name as the old.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy all the data associated with the identified residue to the new, non-existent residue.  The new residue cannot currently exist.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the residue data from residue 1 to the new residue 2, type:")
uf.desc[-1].add_prompt("relax> residue.copy(res_from=':1', res_to=':2')")
uf.desc[-1].add_paragraph("To copy residue 1 of the molecule 'Old mol' to residue 5 of the molecule 'New mol', type:")
uf.desc[-1].add_prompt("relax> residue.copy(res_from='#Old mol:1', res_to='#New mol:5')")
uf.desc[-1].add_paragraph("To copy the residue data of residue 1 from the data pipe 'm1' to 'm2', assuming the current data pipe is 'm1', type:")
uf.desc[-1].add_prompt("relax> residue.copy(res_from=':1', pipe_to='m2')")
uf.desc[-1].add_prompt("relax> residue.copy(pipe_from='m1', res_from=':1', pipe_to='m2', res_to=':1')")
uf.backend = copy_residue
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'residue.png'


# The residue.create user function.
uf = uf_info.add_uf('residue.create')
uf.title = "Create a new residue."
uf.title_short = "Residue creation."
uf.display = True
uf.add_keyarg(
    name = "res_num",
    py_type = "int",
    min = -10000,
    max = 10000,
    desc_short = "residue number",
    desc = "The residue number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_name",
    py_type = "str",
    desc_short = "residue name",
    desc = "The name of the residue.",
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name",
    py_type = "str",
    desc_short = "molecule name",
    desc = "The name of the molecule to add the residue to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_molecule_names,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Using this, a new sequence can be generated without using the sequence user functions.  However if the sequence already exists, the new residue will be added to the end of the residue list (the residue numbers of this list need not be sequential).  The same residue number cannot be used more than once.  A corresponding single spin system will be created for this residue.  The spin system number and name or additional spin systems can be added later if desired.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following sequence of commands will generate the sequence 1 ALA, 2 GLY, 3 LYS:")
uf.desc[-1].add_prompt("relax> residue.create(1, 'ALA')")
uf.desc[-1].add_prompt("relax> residue.create(2, 'GLY')")
uf.desc[-1].add_prompt("relax> residue.create(3, 'LYS')")
uf.backend = create_residue
uf.menu_text = "c&reate"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'residue.png'


# The residue.delete user function.
uf = uf_info.add_uf('residue.delete')
uf.title = "Delete residues from the current data pipe."
uf.title_short = "Residue deletion."
uf.add_keyarg(
    name = "res_id",
    py_type = "str",
    desc_short = "residue ID string",
    desc = "The residue ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_ids,
    wiz_read_only = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This can be used to delete a single or sets of residues.  See the ID string documentation for more information.  If spin system/atom ids are included a RelaxError will be raised.")
uf.desc.append(id_string_doc)
uf.backend = delete_residue
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_height_desc = 550
uf.wizard_size = (900, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'residue.png'


# The residue.display user function.
uf = uf_info.add_uf('residue.display')
uf.title = "Display information about the residue(s)."
uf.display = True
uf.add_keyarg(
    name = "res_id",
    py_type = "str",
    desc_short = "residue ID string",
    desc = "The residue ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_ids,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display the residue data loaded into the current data pipe.")
uf.desc.append(id_string_doc)
uf.backend = display_residue
uf.menu_text = "dis&play"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_height_desc = 550
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'residue.png'


# The residue.name user function.
uf = uf_info.add_uf('residue.name')
uf.title = "Name the residues."
uf.title_short = "Residue naming."
uf.add_keyarg(
    name = "res_id",
    py_type = "str",
    desc_short = "residue ID string",
    desc = "The residue ID string corresponding to one or more residues.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "name",
    py_type = "str",
    desc_short = "new residue name",
    desc = "The new name."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    arg_type = "force flag",
    desc_short = "force flag",
    desc = "A flag which if True will cause the residue to be renamed."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This simply allows residues to be named (or renamed).")
uf.desc.append(id_string_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following sequence of commands will rename the sequence {1 ALA, 2 GLY, 3 LYS} to {1 XXX, 2 XXX, 3 XXX}:")
uf.desc[-1].add_prompt("relax> residue.name(':1', 'XXX', force=True)")
uf.desc[-1].add_prompt("relax> residue.name(':2', 'XXX', force=True)")
uf.desc[-1].add_prompt("relax> residue.name(':3', 'XXX', force=True)")
uf.desc[-1].add_paragraph("Alternatively:")
uf.desc[-1].add_prompt("relax> residue.name(':1,2,3', 'XXX', force=True)")
uf.backend = name_residue
uf.menu_text = "&name"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'residue.png'


# The residue.number user function.
uf = uf_info.add_uf('residue.number')
uf.title = "Number the residues."
uf.title_short = "Residue numbering."
uf.add_keyarg(
    name = "res_id",
    py_type = "str",
    desc_short = "residue ID string",
    desc = "The residue ID string corresponding to a single residue.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "number",
    py_type = "int",
    min = -10000,
    max = 10000,
    desc_short = "new residue number",
    desc = "The new residue number."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    arg_type = "force flag",
    desc_short = "force flag",
    desc = "A flag which if True will cause the residue to be renumbered."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This simply allows residues to be numbered.  The new number cannot correspond to an existing residue.")
uf.desc.append(id_string_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following sequence of commands will renumber the sequence {1 ALA, 2 GLY, 3 LYS} to {101 ALA, 102 GLY, 103 LYS}:")
uf.desc[-1].add_prompt("relax> residue.number(':1', 101, force=True)")
uf.desc[-1].add_prompt("relax> residue.number(':2', 102, force=True)")
uf.desc[-1].add_prompt("relax> residue.number(':3', 103, force=True)")
uf.backend = number_residue
uf.menu_text = "&number"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'residue.png'
