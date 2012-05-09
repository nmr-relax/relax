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
"""Module containing the 'frq' user function data for manipulating spectrometer frequencies."""

# relax module imports.
import generic_fns.frq
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The user function class.
uf_class = uf_info.add_class('frq')
uf_class.title = "Class for manipulating spectrometer frequencies."
uf_class.menu_text = "fr&q"
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
uf.desc = """
This allows the spectrometer frequency of a given experiment to be set.
"""
uf.backend = generic_fns.frq.set
uf.menu_text = "&set"
uf.wizard_size = (700, 400)
