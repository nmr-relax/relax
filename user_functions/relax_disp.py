###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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
"""The relax_disp user function definitions."""

# relax module imports.
from pipe_control import spectrum
from graphics import WIZARD_IMAGE_PATH
from specific_analyses.setup import relax_disp_obj
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('relax_disp')
uf_class.title = "Class for relaxation curve fitting."
uf_class.menu_text = "&relax_disp"
uf_class.gui_icon = "relax.relax_disp"


# The relax_disp.cpmg_delayT user function.
uf = uf_info.add_uf('relax_disp.cpmg_delayT')
uf.title = "Set the CPMG constant time delay (T) of the experiment."
uf.title_short = "CPMG time delay."
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "experiment ID",
    desc = "The experiment identification string."
)
uf.add_keyarg(
    name = "delayT",
    py_type = "float",
    desc_short = "CPMG time delay",
    desc = "The CPMG constant time delay (T) in s."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the CPMG constant time delay (T) of a given experiment to be set.")
uf.backend = relax_disp_obj._cpmg_delayT
uf.menu_text = "&cpmg_delayT"
uf.wizard_size = (800, 500)


# The relax_disp.exp_type user function.
uf = uf_info.add_uf('relax_disp.exp_type')
uf.title = "Select the type of relaxation dispersion experiments to analyse."
uf.title_short = "Relaxation dispersion type selection."
uf.add_keyarg(
    name = "exp",
    default = "cpmg",
    py_type = "str",
    desc_short = "experiment type",
    desc = "The type of relaxation dispersion experiment performed."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The supported experiments will include CPMG ('cpmg') and R1rho ('r1rho').")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick the experiment type 'cpmg' for all selected spins, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type('cpmg')")
uf.desc[-1].add_prompt("relax> relax_disp.exp_type(exp='cpmg')")
uf.backend = relax_disp_obj._exp_type
uf.menu_text = "&exp_type"
uf.wizard_size = (800, 500)


# The relax_disp.select_model user function.
uf = uf_info.add_uf('relax_disp.select_model')
uf.title = "Select the relaxation dispersion curve type."
uf.title_short = "Relaxation dispersion curve type selection."
uf.display = True
uf.add_keyarg(
    name = "model",
    default = "fast",
    py_type = "str",
    desc_short = "model",
    desc = "The type of relaxation dispersion curve to fit (relating to the NMR time scale).",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "fast: [R2, Rex, kex]",
        "slow: [R2A, kA, dw]"
    ],
    wiz_combo_data = [
        "fast",
        "slow"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The supported equations will include the default fast-exchange limit as well as the slow-exchange limit.")
uf.desc[-1].add_paragraph("The parameters of these two models are")
uf.desc[-1].add_item_list_element("'fast'", "[R2, Rex, kex],")
uf.desc[-1].add_item_list_element("'slow'", "[R2A, kA, dw].")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_paragraph("To pick the model 'fast' for all selected spins, type one of:")
uf.desc[-1].add_prompt("relax> relax_disp.select_model('fast')")
uf.desc[-1].add_prompt("relax> relax_disp.select_model(model='fast')")
uf.backend = relax_disp_obj._select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 500)
uf.wizard_apply_button = False
