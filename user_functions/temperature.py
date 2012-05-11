###############################################################################
#                                                                             #
# Copyright (C) 2008-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'temperature' user function data."""

# relax module imports.
from generic_fns import temperature
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


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
uf.desc = """
This allows the temperature of an experiment to be set.  This value should be in Kalvin.  In certain analyses, for example those which use pseudocontact shift data, knowledge of the temperature is essential.  For the pseudocontact shift, the experiment ID string should match one of the alignment IDs.
"""
uf.backend = temperature.set
uf.menu_text = "&temperature"
uf.gui_icon = "oxygen.status.weather-clear"
uf.wizard_size = (700, 500)
