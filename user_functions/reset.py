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

# relax module imports.
import generic_fns.reset
from graphics import WIZARD_IMAGE_PATH
from user_functions.data import Uf_info; uf_info = Uf_info()
from user_functions.objects import Desc_container


# The reset user function.
uf = uf_info.add_uf('reset')
uf.title = "Reinitialise the relax data storage object."
uf.title_short = "Reset relax."
# Description.
uf.desc.append(Desc_container())
uf.desc[-1].add_paragraph("All of the data of the relax data storage object will be erased and hence relax will return to its initial state.")
uf.backend = generic_fns.reset.reset
uf.menu_text = "&reset"
uf.gui_icon = "oxygen.actions.dialog-close"
uf.gui_sync = True    # Force synchronous operation, as asynchronous calls kill the GUI!
uf.wizard_size = (600, 300)
uf.wizard_apply_button = False
uf.wizard_image = WIZARD_IMAGE_PATH + 'reset.png'
