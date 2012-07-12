###############################################################################
#                                                                             #
# Copyright (C) 2003-2012 Edward d'Auvergne                                   #
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
"""The vmd user function definitions for controlling VMD."""

# relax module imports.
from generic_fns import vmd
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container

# The user function class.
uf_class = uf_info.add_class('vmd')
uf_class.title = "Class for interfacing with VMD."
uf_class.menu_text = "&vmd"


# The vmd.view user function.
uf = uf_info.add_uf('vmd.view')
uf.title = "View the structures loaded into the relax data store using VMD."
uf.title_short = "Molecular viewing using VMD."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("This will launch VMD with all of the structures loaded into the relax data store.")
# Prompt examples.
uf.desc.append(Desc_container("Prompt examples"))
uf.desc[-1].add_prompt("relax> vmd.view()")
uf.backend = vmd.view
uf.menu_text = "&view"
uf.wizard_size = (700, 400)
uf.wizard_apply_button = False
