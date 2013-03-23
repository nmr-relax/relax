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
"""The fix user function definitions."""

# relax module imports.
from pipe_control import fix
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The fix user function.
uf = uf_info.add_uf('fix')
uf.title = "Fix or allow parameter values to change during optimisation."
uf.title_short = "Fixing of parameters."
uf.display = True
uf.add_keyarg(
    name = "element",
    py_type = "str",
    desc_short = "element",
    desc = "Which element to fix.",
    wiz_element_type = "combo",
    wiz_combo_choices = [
        "Diffusion tensor parameters",
        "All parameters from all spins",
        "All parameters (diffusion and spin)"],
    wiz_combo_data = [
        "diff",
        "all_spins",
        "all"],
    wiz_read_only = True,
)
uf.add_keyarg(
    name = "fixed",
    default = True,
    py_type = "bool",
    desc_short = "fixed",
    desc = "A flag specifying if the parameters should be fixed or allowed to change."
)
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("The element can be any of the following:")
uf.desc[-1].add_item_list_element("'diff'", "The diffusion tensor parameters.  This will allow all diffusion tensor parameters to be toggled.")
uf.desc[-1].add_item_list_element("'all_spins'", "Using this keyword, all parameters from all spins will be toggled.")
uf.desc[-1].add_item_list_element("'all'", "All parameters will be toggled.  This is equivalent to combining both 'diff' and 'all_spins'.")
uf.desc[-1].add_paragraph("The flag 'fixed', if set to True, will fix parameters during optimisation whereas a value of False will allow parameters to vary.")
uf.backend = fix.fix
uf.menu_text = "&fix"
uf.gui_icon = "oxygen.status.object-locked"
uf.wizard_height_desc = 400
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'object-locked-unlocked.png'
