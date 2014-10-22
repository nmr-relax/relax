###############################################################################
#                                                                             #
# Copyright (C) 2010-2014 Edward d'Auvergne                                   #
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

# Python module imports.
import wx

# GUI module imports.
from gui.uf_objects import build_uf_menus, Uf_storage; uf_store = Uf_storage()
from gui.fonts import font


# Initialise the app.
app = wx.App(0)
app.gui = wx.Dialog(parent=None)

# Set up the required fonts.
font.setup()

# The user function.
uf = uf_store['spin.create']
uf._sync = True
uf.create_wizard(parent=app.gui)

# Show the window.
uf.wizard.Show()
app.MainLoop()
