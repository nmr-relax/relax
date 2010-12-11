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

# Python module imports.
import wx

# relax module imports.
from generic_fns.mol_res_spin import ALLOWED_MOL_TYPES

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
    size_x = 600
    size_y = 400
    frame_title = 'Add a molecule'
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    main_text = 'This dialog allows you to add new molecules to the relax data store.  The molecule will be added to the current data pipe.'
    title = 'Addition of new molecules'

    # Some private class variables.
    _spacing = 20


    def _evt_mol_type(self, event):
        """Selection of the molecule type.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the choice.
        self.mol_type = str(event.GetString())


    def add_uf(self, sizer):
        """Add the molecule specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Spacer.
        sizer.AddSpacer(self._spacing)

        # The molecule name input.
        self.mol_name = self.input_field(sizer, "The name of the molecule:")

        # Spacer.
        sizer.AddSpacer(self._spacing)

        # The type selection.
        self.chooser(sizer, "The type of molecule:", self._evt_mol_type, [''] + ALLOWED_MOL_TYPES)

        # Spacer.
        sizer.AddSpacer(self._spacing)


    def execute(self):
        """Execute the user function."""

        # Get the name and type.
        mol_name = str(self.mol_name.GetValue())

        # Set the name.
        self.interpreter.molecule.create(mol_name=mol_name, type=self.mol_type)
