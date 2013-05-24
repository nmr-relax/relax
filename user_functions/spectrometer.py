###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
"""The spectrometer user function definitions for loading spectrometer information."""

# relax module imports.
import pipe_control.spectrometer
from pipe_control import spectrum
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The user function class.
uf_class = uf_info.add_class('spectrometer')
uf_class.title = "Class for manipulating spectrometer frequencies."
uf_class.menu_text = "&spectrometer"
uf_class.gui_icon = "relax.spectrometer"

# The spectrometer.frequency user function.
uf = uf_info.add_uf('spectrometer.frequency')
uf.title = "Set the spectrometer proton frequency of the experiment."
uf.title_short = "Spectrometer frequency setup."
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "experiment ID",
    desc = "The experiment identification string to set the frequency of.",
    wiz_element_type = 'combo',
    wiz_combo_iter = spectrum.get_ids
)
uf.add_keyarg(
    name = "frq",
    py_type = "num",
    desc_short = "spectrometer frequency",
    desc = "The spectrometer frequency.  See the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file."
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
        "kHz",
        "MHz",
        "GHz"
    ],
    wiz_read_only = False
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the spectrometer frequency of a given experiment to be set.  The expected units are that of the proton resonance frequency in Hertz.  See the 'sfrq' parameter in the Varian procpar file or the 'SFO1' parameter in the Bruker acqus file for the exact value.")
uf.backend = pipe_control.spectrometer.set_frequency
uf.menu_text = "&frequency"
uf.gui_icon = "relax.frq"
uf.wizard_size = (750, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'spectrometer.png'


# The spectrometer.temperature user function.
uf = uf_info.add_uf('spectrometer.temperature')
uf.title = "Specify the temperature of an experiment."
uf.title_short = "Experimental temperature."
uf.add_keyarg(
    name = "id",
    py_type = "str",
    desc_short = "experiment ID string",
    desc = "The experiment identification string."
)
uf.add_keyarg(
    name = "temp",
    py_type = "num",
    desc_short = "experimental temperature",
    desc = "The temperature of the experiment in Kalvin."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This allows the temperature of an experiment to be set.  This value should be in Kalvin.  In certain analyses, for example those which use pseudocontact shift data, knowledge of the temperature is essential.  For the pseudocontact shift, the experiment ID string should match one of the alignment IDs.")
uf.backend = pipe_control.spectrometer.set_temperature
uf.menu_text = "&temperature"
uf.gui_icon = "oxygen.status.weather-clear"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'oxygen-icon-weather-snow-scattered-night.png'
