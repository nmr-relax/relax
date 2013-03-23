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
"""The temperature user function definitions."""

# relax module imports.
from pipe_control import temperature
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The temperature user function.
uf = uf_info.add_uf('temperature')
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
uf.backend = temperature.set
uf.menu_text = "&temperature"
uf.gui_icon = "oxygen.status.weather-clear"
uf.wizard_size = (700, 500)
uf.wizard_image = WIZARD_IMAGE_PATH + 'oxygen-icon-weather-snow-scattered-night.png'
