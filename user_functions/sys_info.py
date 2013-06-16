###############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
"""The sys_info user function definitions."""

# relax module imports.
from info import print_sys_info
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The sys_info user function.
uf = uf_info.add_uf('sys_info')
uf.title = "Display all system information relating to this version of relax."
uf.title_short = "Display system information."
uf.display = True
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will display all of the relax, Python, python package and hardware information currently being used by relax.  This is useful for seeing if all packages are up to date and if the correct software versions are being used.  It is also very useful information for reporting relax bugs.")
uf.backend = print_sys_info
uf.menu_text = "s&ys_info"
uf.gui_icon = "oxygen.actions.help-about"
uf.wizard_size = (700, 400)
uf.wizard_apply_button = False
