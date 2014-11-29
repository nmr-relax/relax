###############################################################################
#                                                                             #
# Copyright (C) 2004-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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
"""The relax_fit user function definitions."""

# Python module imports.
from os import sep

# relax module imports.
from graphics import ANALYSIS_IMAGE_PATH
from lib.text.gui import i0, iinf, rx
from pipe_control import spectrum
from specific_analyses.relax_fit.uf import relax_time, select_model
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
uf.backend = relax_time
uf.menu_text = "&relax_time"
uf.gui_icon = "oxygen.actions.chronometer"
uf.wizard_size = (700, 500)
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'r1_200x200.png'


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
        "Two parameter exponential fit: [%s, %s]" % (rx, i0),
        "Inversion recovery: [%s, %s, %s]" % (rx, i0, iinf),
        "Saturation recovery: [%s, %s]" % (rx, iinf)
    ],
    wiz_combo_data = [
        "exp",
        "inv",
        "sat"
    ],
    wiz_read_only = True
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("A number of relaxation experiments are supported and include:")
uf.desc[-1].add_paragraph("The 'exp' model.  This is the default two parameter exponential fit.  The magnetisation starts at I0 and decays to zero.  The parameters are [Rx, I0] and the equation is I(t) = I0*exp(-Rx*t).")
uf.desc[-1].add_paragraph("The 'inv' model.  This is the inversion recovery experiment (IR).  The magnetisation starts at a negative value at -I0 and relaxes to a positive Iinf value.  The parameters are [Rx, I0, Iinf] and the equation is I(t) = Iinf - I0*exp(-Rx*t).  This has not been implemented yet.")
uf.desc[-1].add_paragraph("The 'sat' model.  This is the saturation recovery experiment (SR).  The magnetisation starts at zero and relaxes to a positive Iinf value.  The parameters are [Rx, Iinf] and the equation is I(t) = Iinf*(1 - exp(-Rx*t)).")
uf.backend = select_model
uf.menu_text = "&select_model"
uf.gui_icon = "oxygen.actions.list-add"
uf.wizard_height_desc = 500
uf.wizard_size = (900, 600)
uf.wizard_apply_button = False
uf.wizard_image = ANALYSIS_IMAGE_PATH + 'r1_200x200.png'
