###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""The interatomic user function definitions."""

# Python module imports.
from os import sep

# relax module imports.
from generic_fns.mol_res_spin import get_spin_ids
from generic_fns import pipes
from generic_fns.interatomic import copy, create_interatom
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('interatomic')
uf_class.title = "Class for manipulating the interatomic data."
uf_class.menu_text = "&interatomic"
uf_class.gui_icon = "relax.dipole_pair"


# The interatomic.copy user function.
uf = uf_info.add_uf('interatomic.copy')
uf.title = "Copy all data associated with a interatomic data container."
uf.title_short = "Spin copying."
uf.display = True
uf.add_keyarg(
    name = "pipe_from",
    py_type = "str",
    desc_short = "source data pipe",
    desc = "The data pipe containing the interatomic data container from which the data will be copied.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe_to",
    py_type = "str",
    desc_short = "destination data pipe",
    desc = "The data pipe to copy the interatomic data container to.  This defaults to the current data pipe.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id1",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id2",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will copy all the data associated with the identified interatomic data container to a different data pipe.  The new interatomic data container must not already exist.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To copy the interatomic data container between ':2@C' and ':2@H', from the 'orig' data pipe to the current data pipe, type one of:")
uf.desc[-1].add_prompt("relax> interatomic.copy('orig', spin_id1=':2@C', spin_id2=':2@H')")
uf.desc[-1].add_prompt("relax> interatomic.copy(pipe_from='orig', spin_id1=':2@C', spin_id2=':2@H')")
uf.backend = copy
uf.menu_text = "&copy"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_size = (700, 600)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'


# The interatomic.create user function.
uf = uf_info.add_uf('interatomic.create')
uf.title = "Create a new spin."
uf.title_short = "Spin creation."
uf.display = True
uf.add_keyarg(
    name = "spin_id1",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "first spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "spin_id2",
    py_type = "str",
    arg_type = "spin ID",
    desc_short = "second spin ID",
    desc = "The spin ID of the first spin.",
    wiz_combo_iter = get_spin_ids,
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe",
    py_type = "str",
    desc_short = "alternative data pipe",
    desc = "The data pipe to create the interatomic data container for.  This defaults to the current data pipe if not supplied.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    wiz_read_only = True,
    can_be_none = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will add a new interatomic data container connecting two existing spins to the relax data storage object.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To connect the spins ':1@N' to ':1@H', type one of:")
uf.desc[-1].add_prompt("relax> interatomic.create(':1@N', ':1@H')")
uf.desc[-1].add_prompt("relax> interatomic.create(spin_id1=':1@N', spin_id2=':1@H')")
uf.backend = create_interatom
uf.menu_text = "c&reate"
uf.gui_icon = "oxygen.actions.list-add-relax-blue"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'dipole_pair' + sep + 'NH_dipole_pair.png'
