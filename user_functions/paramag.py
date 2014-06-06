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
"""The paramag user function definitions for paramagnetic related functions."""

# relax module imports.
from graphics import WIZARD_IMAGE_PATH
from pipe_control import paramag, pipes
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('paramag')
uf_class.title = "Class for handling paramagnetic information."
uf_class.menu_text = "&paramag"
uf_class.gui_icon = "relax.align_tensor"


# The paramag.centre user function.
uf = uf_info.add_uf('paramag.centre')
uf.title = "Specify which atom is the paramagnetic centre."
uf.title_short = "Paramagnetic centre selection."
uf.add_keyarg(
    name = "pos",
    py_type = "num_list",
    dim = 3,
    desc_short = "atomic position",
    desc = "The atomic position of the paramagnetic centre.",
    list_titles = ['X coordinate', 'Y coordinate', 'Z coordinate'],
    can_be_none = True
)
uf.add_keyarg(
    name = "atom_id",
    py_type = "str",
    desc_short = "atom ID string",
    desc = "The atom ID string.",
    can_be_none = True
)
uf.add_keyarg(
    name = "pipe",
    py_type = "str",
    desc_short = "data pipe",
    desc = "The data pipe containing the structures to extract the centre from.",
    wiz_element_type = 'combo',
    wiz_combo_iter = pipes.pipe_names,
    can_be_none = True
)
uf.add_keyarg(
    name = "verbosity",
    default = 1,
    py_type = "int",
    desc_short = "verbosity level",
    desc = "The amount of information to print out."
)
uf.add_keyarg(
    name = "fix",
    default = True,
    py_type = "bool",
    desc_short = "fix flag",
    desc = "A flag specifying if the paramagnetic centre should be fixed during optimisation."
)
uf.add_keyarg(
    name = "ave_pos",
    default = True,
    py_type = "bool",
    desc_short = "average position flag",
    desc = "A flag specifying if the position of the atom is to be averaged across all models."
)
uf.add_keyarg(
    name = "force",
    default = False,
    py_type = "bool",
    desc_short = "force flag",
    desc = "A flag which if True will cause the current paramagnetic centre to be overwritten."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This is required for specifying where the paramagnetic centre is located in the loaded structure file.  If no structure number is given, then the average atom position will be calculated if multiple structures are loaded.")
uf.desc[-1].add_paragraph("A different set of structures than those loaded into the current data pipe can also be used to determine the position, or its average.  This can be achieved by loading the alternative structures into another data pipe, and then specifying that pipe.")
uf.desc[-1].add_paragraph("If the average position flag is set to True, the average position from all models will be used as the position of the paramagnetic centre.  If False, then the positions from all structures will be used.  If multiple positions are used, then a fast paramagnetic centre motion will be assumed so that PCSs for a single tensor will be calculated for each position, and the PCS values linearly averaged.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("If the paramagnetic centre is the lanthanide Dysprosium which is labelled as Dy in a loaded PDB file, then type one of:")
uf.desc[-1].add_prompt("relax> paramag.centre('Dy')")
uf.desc[-1].add_prompt("relax> paramag.centre(atom_id='Dy')")
uf.desc[-1].add_paragraph("If the carbon atom 'C1' of residue '4' in the PDB file is to be used as the paramagnetic centre, then type:")
uf.desc[-1].add_prompt("relax> paramag.centre(':4@C1')")
uf.desc[-1].add_paragraph("To state that the Dy3+ atomic position is [0.136, 12.543, 4.356], type one of:")
uf.desc[-1].add_prompt("relax> paramag.centre([0.136, 12.543, 4.356])")
uf.desc[-1].add_prompt("relax> paramag.centre(pos=[0.136, 12.543, 4.356])")
uf.desc[-1].add_paragraph("To find an unknown paramagnetic centre, type:")
uf.desc[-1].add_prompt("relax> paramag.centre(fix=False)")
uf.backend = paramag.centre
uf.menu_text = "&centre"
uf.wizard_height_desc = 400
uf.wizard_size = (1000, 750)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'align_tensor.png'
