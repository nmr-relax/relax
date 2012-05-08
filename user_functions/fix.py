###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""Module containing the 'fix' user function data."""

# relax module imports.
from generic_fns import fix
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


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
uf.desc = """
The keyword argument 'element' can be any of the following:

    'diff' - the diffusion tensor parameters.  This will allow all diffusion tensor parameters to be toggled.
    
    'all_spins' - using this keyword, all parameters from all spins will be toggled.
    
    'all' - all parameters will be toggled.  This is equivalent to combining both 'diff' and 'all_spins'.

The flag 'fixed', if set to True, will fix parameters during optimisation whereas a value of False will allow parameters to vary.
"""
uf.backend = fix.fix
uf.menu_text = "&fix"
uf.gui_icon = "oxygen.status.object-locked"
uf.wizard_height_desc = 400
uf.wizard_size = (800, 600)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'object-locked-unlocked.png'
