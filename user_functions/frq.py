###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
"""The frq user function definitions for manipulating spectrometer frequencies."""

# relax module imports.
import generic_fns.frq
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('frq')
uf_class.title = "Class for manipulating spectrometer frequencies."
uf_class.menu_text = "&frq"
uf_class.gui_icon = "relax.frq"

# The frq.set user function.
uf = uf_info.add_uf('frq.set')
uf.title = "Set the spectrometer frequency of the experiment."
uf.title_short = "Spectrometer frequency setting."
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "experiment ID",
    desc = "The experiment identification string."
)
uf.add_keyarg(
    name = "frq",
    py_type = "num",
    desc_short = "spectrometer frequency",
    desc = "The spectrometer frequency in Hertz."
)
uf.add_keyarg(
    name = "units",
    default = "Hz",
    py_type = "str",
    desc_short = "frequency units",
    desc = "The units of frequency.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "Hz",
        "kHz"
        "MHz"
        "GHz"
    ],
    wiz_read_only = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the spectrometer frequency of a given experiment to be set.  The expected units are that of the proton resonance frequency in Hertz.  See the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file for the exact value.")
uf.backend = generic_fns.frq.set
uf.menu_text = "&set"
uf.gui_icon = "oxygen.actions.edit-rename"
uf.wizard_size = (750, 500)
