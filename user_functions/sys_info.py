###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""The sys_info user function definitions."""

# relax module imports.
from generic_fns.sys_info import sys_info
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()


# The sys_info user function.
uf = uf_info.add_uf('sys_info')
uf.title = "Display all system information relating to this version of relax."
uf.title_short = "Display system information."
uf.display = True
uf.desc = """
This will display all of the relax, Python, python package and hardware information currently being used by relax.  This is useful for seeing if all packages are up to date and if the correct software versions are being used.  It is also very useful information for reporting relax bugs.
"""
uf.backend = sys_info
uf.menu_text = "s&ys_info"
uf.gui_icon = "oxygen.actions.help-about"
uf.wizard_apply_button = False
