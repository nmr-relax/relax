###############################################################################
#                                                                             #
# Copyright (C) 2007-2012 Edward d'Auvergne                                   #
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
"""The spin user function definitions."""

# relax module imports.
from generic_fns.mol_res_spin import copy_spin, create_pseudo_spin, create_spin, delete_spin, display_spin, get_molecule_names, get_residue_ids, get_residue_names, get_residue_nums, get_spin_ids, id_string_doc, name_spin, number_spin, set_spin_element
from generic_fns import pipes
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('spin')
uf_class.title = "Class for manipulating the spin data."
uf_class.menu_text = "&spin"
uf_class.gui_icon = "relax.spin"


# The spin.copy user function.
uf = uf_info.add_uf('spin.copy')
uf.title = "Copy all data associated with a spin."
uf.title_short = "Spin copying."
uf.display = True
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The data pipe containing the spin from which the data will be copied.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_from",
    py_type = "str",
    desc_short = "source spin ID",
    desc = "The spin identifier string of the spin to copy the data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_spin_ids,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The data pipe to copy the data to.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_to",
    py_type = "str",
    desc_short = "destination spin ID",
    desc = "The spin identifier string of the spin to copy the data to.  If left blank, the new spin will have the same name as the old.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy all the data associated with the identified spin to the new, non-existent spin.  The new spin must not already exist.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the spin data from spin 1 to the new spin 2, type:")
uf.desc[-1].add_prompt("relax> spin.copy(spin_from='@1', spin_to='@2')")
uf.desc[-1].add_paragraph("To copy spin 1 of the molecule 'Old mol' to spin 5 of the molecule 'New mol', type:")
uf.desc[-1].add_prompt("relax> spin.copy(spin_from='#Old mol@1', spin_to='#New mol@5')")
uf.desc[-1].add_paragraph("To copy the spin data of spin 1 from the data pipe 'm1' to 'm2', assuming the current data pipe is 'm1', type:")
uf.desc[-1].add_prompt("relax> spin.copy(spin_from='@1', pipe_to='m2')")
uf.desc[-1].add_prompt("relax> spin.copy(pipe_from='m1', spin_from='@1', pipe_to='m2', spin_to='@1')")
uf.backend = copy_spin
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (700, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'


# The spin.create user function.
uf = uf_info.add_uf('spin.create')
uf.title = "Create a new spin."
uf.title_short = "Spin creation."
uf.display = True
uf.add_keyarg(
    name = "spin_name",
    py_type = "str",
    desc_short = "spin name",
    desc = "The name of the spin.",
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_num",
    py_type = "int",
    min = -10000,
    max = 10000,
    desc_short = "spin number",
    desc = "The spin number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_name",
    py_type = "str",
    desc_short = "residue name",
    desc = "The name of the residue to add the spin to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "res_num",
    py_type = "int",
    desc_short = "residue number",
    desc = "The number of the residue to add the spin to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_nums,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_name",
    py_type = "str",
    desc_short = "molecule name",
    desc = "The name of the molecule to add the spin to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_molecule_names,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will add a new spin data container to the relax data storage object.  The same spin number cannot be used more than once.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following sequence of commands will generate the sequence 1 C4, 2 C9, 3 C15:")
uf.desc[-1].add_prompt("relax> spin.create(1, 'C4')")
uf.desc[-1].add_prompt("relax> spin.create(2, 'C9')")
uf.desc[-1].add_prompt("relax> spin.create(3, 'C15')")
uf.backend = create_spin
uf.menu_text = "c&reate"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'


# The spin.create_pseudo user function.
uf = uf_info.add_uf('spin.create_pseudo')
uf.title = "Create a spin system representing a pseudo-atom."
uf.title_short = "Pseudo-atom creation."
uf.add_keyarg(
    name = "spin_name",
    py_type = "str",
    desc_short = "spin name",
    desc = "The name of the pseudo-atom spin."
)
uf.add_keyarg(
    name = "spin_num",
    py_type = "int",
    min = -10000,
    max = 10000,
    desc_short = "spin number",
    desc = "The spin number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "res_id",
    py_type = "str",
    desc_short = "residue ID string",
    desc = "The molecule and residue ID string identifying the position to add the pseudo-spin to.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_residue_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "members",
    py_type = "str_list",
    desc_short = "members",
    desc = "A list of the atoms (as spin ID strings) that the pseudo-atom is composed of.",
    wiz_element_type = "combo_list",
    wiz_combo_iter = get_spin_ids,
    wiz_combo_list_min = 2,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "averaging",
    default = "linear",
    py_type = "str",
    desc_short = "positional averaging",
    desc = "The positional averaging technique.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["linear"],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will create a spin data container representing a number of pre-existing spin containers as a pseudo-atom.  The optional spin number must not already exist.")
uf.desc.append(id_string_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following will create the pseudo-atom named 'Q9' consisting of the protons '@H16', '@H17', '@H18':")
uf.desc[-1].add_prompt("relax> spin.create_pseudo('Q9', members=['@H16', '@H17', '@H18'])")
uf.backend = create_pseudo_spin
uf.menu_text = "create_p&seudo"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_height_desc = 350
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'


# The spin.delete user function.
uf = uf_info.add_uf('spin.delete')
uf.title = "Delete spins."
uf.title_short = "Spin deletion."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identifier string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_spin_ids
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This can be used to delete a single or sets of spins.  See the identification string documentation below for more information.")
uf.desc.append(id_string_doc)
uf.backend = delete_spin
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_height_desc = 550
uf.wizard_size = (900, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'


# The spin.display user function.
uf = uf_info.add_uf('spin.display')
uf.title = "Display information about the spin(s)."
uf.title_short = "Spin information."
uf.display = True
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display the spin data loaded into the current data pipe.")
uf.desc.append(id_string_doc)
uf.backend = display_spin
uf.menu_text = "dis&play"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'


# The spin.element user function.
uf = uf_info.add_uf('spin.element')
uf.title = "Set the element type of the spin."
uf.title_short = "Spin element setting."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string corresponding to one or more spins.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "element",
    py_type = "str",
    desc_short = "IUPAC element name",
    desc = "The IUPAC element name.",
    wiz_element_type = "combo",
    wiz_combo_choices = ["N", "C", "H", "O", "P"]
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    arg_type = "force flag",
    desc_short = "force flag",
    desc = "A flag which if True will cause the element to be changed."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the element type of the spins to be set.")
uf.desc.append(id_string_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The set all spins of residue 1 to be carbons, type one of:")
uf.desc[-1].add_prompt("relax> spin.element('@1', 'C', force=True)")
uf.desc[-1].add_prompt("relax> spin.element(spin_id='@1', element='C', force=True)")
uf.backend = set_spin_element
uf.menu_text = "&element"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (900, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'


# The spin.name user function.
uf = uf_info.add_uf('spin.name')
uf.title = "Name the spins."
uf.title_short = "Spin naming."
uf.add_keyarg(
    name = "name",
    py_type = "str",
    desc_short = "new spin name",
    desc = "The new name."
)
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "spin ID string",
    desc = "The spin identification string corresponding to one or more spins.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    arg_type = "force flag",
    desc_short = "force flag",
    desc = "A flag which if True will cause the spin to be renamed."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This simply allows spins to be named (or renamed).  Spin naming often essential.  For example when reading Sparky peak list files, then the spin name must match that in the file.")
uf.desc.append(id_string_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following sequence of commands will rename the sequence {1 C1, 2 C2, 3 C3} to {1 C11, 2 C12, 3 C13}:")
uf.desc[-1].add_prompt("relax> spin.name('@1', 'C11', force=True)")
uf.desc[-1].add_prompt("relax> spin.name('@2', 'C12', force=True)")
uf.desc[-1].add_prompt("relax> spin.name('@3', 'C13', force=True)")
uf.backend = name_spin
uf.menu_text = "&name"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'


# The spin.number user function.
uf = uf_info.add_uf('spin.number')
uf.title = "Number the spins."
uf.title_short = "Spin numbering."
uf.add_keyarg(
    name = "spin_id",
    py_type = "str",
    desc_short = "spin ID string",
    desc = "The spin identification string corresponding to a single spin.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "number",
    py_type = "int",
    min = -10000,
    max = 10000,
    desc_short = "new spin number",
    desc = "The new spin number.",
    can_be_none = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    arg_type = "force flag",
    desc_short = "force flag",
    desc = "A flag which if True will cause the spin to be renumbered."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This simply allows spins to be numbered.  The new number cannot correspond to an existing spin number.")
uf.desc.append(id_string_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("The following sequence of commands will renumber the sequence {1 C1, 2 C2, 3 C3} to {-1 C1, -2 C2, -3 C3}:")
uf.desc[-1].add_prompt("relax> spin.number('@1', -1, force=True)")
uf.desc[-1].add_prompt("relax> spin.number('@2', -2, force=True)")
uf.desc[-1].add_prompt("relax> spin.number('@3', -3, force=True)")
uf.backend = number_spin
uf.menu_text = "num&ber"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 500
uf.wizard_size = (1000, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spin.png'
