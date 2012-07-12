###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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
"""The splitter window element to hold the tree view and containers."""


# Python module imports.
import wx

# GUI module imports.
from gui.spin_viewer.containers import Container
from gui.spin_viewer.tree import Mol_res_spin_tree


class Tree_splitter(wx.SplitterWindow):
    """This splits the view of the tree view and spin container."""

    def __init__(self, gui, parent, id):
        """Initialise the tree splitter window.

        @param gui:     The gui object.
        @type gui:      wx object
        @param parent:  The parent wx object.
        @type parent:   wx object
        @param id:      The ID number.
        @type id:       int
        """

        # Execute the base class __init__() method.
        wx.SplitterWindow.__init__(self, parent, id, style=wx.SP_LIVE_UPDATE)

        # Add the tree view panel.
        parent.tree_panel = Mol_res_spin_tree(gui, parent=self, id=-1)

        # The container window.
        parent.container = Container(gui, parent=self, id=-1)

        # Make sure the panes cannot be hidden.
        self.SetMinimumPaneSize(100)

        # Split.
        self.SplitVertically(parent.tree_panel, parent.container, 400)
