###############################################################################
#                                                                             #
# Copyright (C) 2004-2012 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""The relax_fit user function definitions."""

# relax module imports.
from generic_fns import spectrum
from graphics import WIZARD_IMAGE_PATH
from specific_fns.setup import relax_fit_obj
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('relax_fit')
uf_class.title = "Class for relaxation curve fitting."
uf_class.menu_text = "&relax_fit"
uf_class.gui_icon = "relax.relax_fit"


# The relax_fit.relax_time user function.
uf = uf_info.add_uf('relax_fit.relax_time')
uf.title = "Set the relaxation delay time associated with each spectrum."
uf.title_short = "Relaxation delay time setting."
uf.add_keyarg(
    name = "time",
    default = 0.0,
    py_type = "num",
    desc_short = "relaxation time",
    desc = "The time, in seconds, of the relaxation period."
)
uf.add_keyarg(
    name = "spectrum_id",
    py_type = "str",
    desc_short = "spectrum identification string",
    desc = "The spectrum identification string.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids,
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("Peak intensities should be loaded before calling this user function via the spectrum.read_intensities user function.  The intensity values will then be associated with a spectrum identifier.  To associate each spectrum identifier with a time point in the relaxation curve prior to optimisation, this user function should be called.")
uf.backend = relax_fit_obj._relax_time
uf.menu_text = "&relax_time"
uf.gui_icon = "oxygen.actions.chronometer"
uf.wizard_size = (700, 500)


# The relax_fit.select_model user function.
uf = uf_info.add_uf('relax_fit.select_model')
uf.title = "Select the relaxation curve type."
uf.title_short = "Relaxation curve type selection."
uf.display = True
uf.add_keyarg(
    name = "model",
    default = "exp",
    py_type = "str",
    desc_short = "model",
    desc = "The type of relaxation curve to fit.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "exp: [Rx, I0]",
        "inv: [Rx, I0, Iinf]"
    ],
    wiz_combo_data = [
        "exp",
        "inv"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The supported relaxation experiments include the default two parameter exponential fit, selected by setting the model type to 'exp', and the three parameter inversion recovery experiment in which the peak intensity limit is a non-zero value, selected by setting the model to 'inv'.")
uf.desc[-1].add_paragraph("The parameters of these two models are")
uf.desc[-1].add_item_list_element("'exp'", "[Rx, I0],")
uf.desc[-1].add_item_list_element("'inv'", "[Rx, I0, Iinf].")
uf.backend = relax_fit_obj._select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 300
uf.wizard_size = (800, 500)
uf.wizard_apply_button = False
