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
"""The molecule user function definitions."""

# relax module imports.
from generic_fns.mol_res_spin import ALLOWED_MOL_TYPES, copy_molecule, create_molecule, delete_molecule, display_molecule, get_molecule_ids, id_string_doc, name_molecule, type_molecule
from generic_fns import pipes
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('molecule')
uf_class.title = "Class for manipulating the molecule data."
uf_class.menu_text = "&molecule"
uf_class.gui_icon = "relax.molecule"


# The molecule.copy user function.
uf = uf_info.add_uf('molecule.copy')
uf.title = "Copy all data associated with a molecule."
uf.title_short = "Molecule copying."
uf.display = True
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The data pipe containing the molecule from which the data will be copied.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "mol_from",
    py_type = "str",
    desc_short = "source molecule ID",
    desc = "The name of the molecule from which to copy data from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_molecule_ids,
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
    name = "mol_to",
    py_type = "str",
    desc_short = "destination molecule ID",
    desc = "The name of the new molecule.  If left blank, the new molecule will have the same name as the old.  This needs to be a molecule ID string, starting with '#'.",
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy all the data associated with a molecule to a second molecule.  This includes all residue and spin system information.  The new molecule name must be unique in the destination data pipe.")
uf.desc.append(id_string_doc)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the molecule data from the molecule 'GST' to the new molecule 'wt-GST', type:")
uf.desc[-1].add_prompt("relax> molecule.copy('#GST', '#wt-GST')")
uf.desc[-1].add_prompt("relax> molecule.copy(mol_from='#GST', mol_to='#wt-GST')")
uf.desc[-1].add_paragraph("To copy the molecule data of the molecule 'Ap4Aase' from the data pipe 'm1' to 'm2', assuming the current data pipe is 'm1', type:")
uf.desc[-1].add_prompt("relax> molecule.copy(mol_from='#ApAase', pipe_to='m2')")
uf.desc[-1].add_prompt("relax> molecule.copy(pipe_from='m1', mol_from='#ApAase', pipe_to='m2', mol_to='#ApAase')")
uf.backend = copy_molecule
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 600
uf.wizard_size = (1000, 800)
uf.wizard_image = WIZARD_IMAGE_PATH + 'molecule.png'


# The molecule.create user function.
uf = uf_info.add_uf('molecule.create')
uf.title = "Create a new molecule."
uf.title_short = "Molecule creation."
uf.display = True
uf.add_keyarg(
    name = "mol_name",
    py_type = "str",
    desc_short = "molecule name",
    desc = "The name of the new molecule."
)
uf.add_keyarg(
    name = "mol_type",
    py_type = "str",
    desc_short = "molecule type",
    desc = "The type of molecule.",
    wiz_element_type = "combo",
    wiz_combo_choices = ALLOWED_MOL_TYPES,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
text = "This adds a new molecule data container to the relax data storage object.  The same molecule name cannot be used more than once.  The molecule type need not be specified.  However, if given, it should be one of"
for i in range(len(ALLOWED_MOL_TYPES)-1):
    text += " '%s'," % ALLOWED_MOL_TYPES[i]
text += " or '%s'." % ALLOWED_MOL_TYPES[-1]
uf.desc[-1].add_paragraph(text)
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To create the molecules 'Ap4Aase', 'ATP', and 'MgF4', type:")
uf.desc[-1].add_prompt("relax> molecule.create('Ap4Aase')")
uf.desc[-1].add_prompt("relax> molecule.create('ATP')")
uf.desc[-1].add_prompt("relax> molecule.create('MgF4')")
uf.backend = create_molecule
uf.menu_text = "c&reate"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (700, 400)
uf.wizard_image = WIZARD_IMAGE_PATH + 'molecule.png'


# The molecule.delete user function.
uf = uf_info.add_uf('molecule.delete')
uf.title = "Deleting molecules from the relax data store."
uf.title_short = "Molecule deletion."
uf.add_keyarg(
    name = "mol_id",
    py_type = "str",
    desc_short = "molecule ID string",
    desc = "The molecule ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_molecule_ids,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This can be used to delete a single or sets of molecules from the relax data store.  The molecule will be deleted from the current data pipe.")
uf.desc.append(id_string_doc)
uf.backend = delete_molecule
uf.menu_text = "&delete"
uf.gui_icon = "oxygen.actions.list-remove"
uf.wizard_height_desc = 550
uf.wizard_size = (900, 750)
uf.wizard_image = WIZARD_IMAGE_PATH + 'molecule.png'


# The molecule.display user function.
uf = uf_info.add_uf('molecule.display')
uf.title = "Display the molecule information."
uf.title_short = "Molecule information."
uf.display = True
uf.add_keyarg(
    name = "mol_id",
    py_type = "str",
    desc_short = "molecule ID string",
    desc = "The molecule ID string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_molecule_ids,
    wiz_read_only = True,
    can_be_none = True
)
uf.desc.append(id_string_doc)
uf.backend = display_molecule
uf.menu_text = "dis&play"
uf.gui_icon = "oxygen.actions.document-preview"
uf.wizard_height_desc = 400
uf.wizard_size = (900, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'molecule.png'


# The molecule.name user function.
uf = uf_info.add_uf('molecule.name')
uf.title = "Name a molecule."
uf.add_keyarg(
    name = "mol_id",
    py_type = "str",
    desc_short = "molecule ID string",
    desc = "The molecule ID string corresponding to one or more molecules.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_molecule_ids,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "name",
    py_type = "str",
    desc_short = "new molecule name",
    desc = "The new molecule name."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the molecule to be renamed."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This simply allows molecules to be named (or renamed).")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To rename the molecule 'Ap4Aase' to 'Inhib Ap4Aase', type one of:")
uf.desc[-1].add_prompt("relax> molecule.name('#Ap4Aase', 'Inhib Ap4Aase', True)")
uf.desc[-1].add_prompt("relax> molecule.name(mol_id='#Ap4Aase', name='Inhib Ap4Aase', force=True)")
uf.desc[-1].add_paragraph("This assumes the molecule 'Ap4Aase' already exists.")
uf.desc.append(id_string_doc)
uf.backend = name_molecule
uf.menu_text = "&name"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 550
uf.wizard_size = (1000, 720)
uf.wizard_image = WIZARD_IMAGE_PATH + 'molecule.png'


# The molecule.type user function.
uf = uf_info.add_uf('molecule.type')
uf.title = "Set the molecule type."
uf.title_short = "Setting molecule type."
uf.add_keyarg(
    name = "mol_id",
    py_type = "str",
    desc_short = "molecule ID string",
    desc = "The molecule ID string corresponding to one or more molecules.",
    wiz_element_type = 'combo',
    wiz_combo_iter = get_molecule_ids,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "type",
    py_type = "str",
    desc_short = "molecule type",
    desc = "The molecule type.",
    wiz_element_type = "combo",
    wiz_combo_choices = ALLOWED_MOL_TYPES,
    wiz_read_only = True
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the molecule to type to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the type of the molecule to be specified.  It can be one of:")
for i in range(len(ALLOWED_MOL_TYPES)-1):
    uf.desc[-1].add_list_element("'%s'," % ALLOWED_MOL_TYPES[i])
uf.desc[-1].add_list_element("'%s'." % ALLOWED_MOL_TYPES[-1])
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To set the molecule 'Ap4Aase' to the 'protein' type, type one of:")
uf.desc[-1].add_prompt("relax> molecule.type('#Ap4Aase', 'protein', True)")
uf.desc[-1].add_prompt("relax> molecule.type(mol_id='#Ap4Aase', type='protein', force=True)")
uf.desc.append(id_string_doc)
uf.backend = type_molecule
uf.menu_text = "&type"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'molecule.png'
