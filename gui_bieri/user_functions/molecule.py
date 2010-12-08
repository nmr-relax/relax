###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""The molecule user function GUI elements."""

# GUI module imports.
from base import UF_base, UF_window
from gui_bieri.paths import WIZARD_IMAGE_PATH


# The container class.
class Molecule(UF_base):
    """The container class for holding all GUI elements."""

    def setup(self):
        """Place all the GUI classes into this class for storage."""

        # The dialogs.
        self._add_window = Add_window(self.gui, self.interpreter)


    def add(self, event):
        """The molecule.add user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._add_window.Show()


    def destroy(self):
        """Close all windows."""

        self._add_window.Destroy()


class Add_window(UF_window):
    """The molecule.add() user function window."""

    # Some class variables.
    size_x = 400
    size_y = 400
    border = 5
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    title = 'Molecule addition'
