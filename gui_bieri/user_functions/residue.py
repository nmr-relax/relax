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
"""The residue user function GUI elements."""

# Python module imports.
from string import split
import wx

# relax module imports.
from generic_fns.mol_res_spin import molecule_loop, residue_loop
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_window
from gui_bieri.paths import WIZARD_IMAGE_PATH


# The container class.
class Residue(UF_base):
    """The container class for holding all GUI elements."""

    def setup(self):
        """Place all the GUI classes into this class for storage."""

        # The dialogs.
        self._create_window = Add_window(self.gui, self.interpreter)
        self._delete_window = Delete_window(self.gui, self.interpreter)


    def create(self, event):
        """The residue.create user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._create_window.Show()


    def delete(self, event):
        """The residue.delete user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._delete_window.Show()


    def destroy(self):
        """Close all windows."""

        self._create_window.Destroy()
        self._delete_window.Destroy()



class Add_window(UF_window):
    """The residue.create() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Add a residue'
    image_path = WIZARD_IMAGE_PATH + 'residue.png'
    main_text = 'This dialog allows you to add new residues to the relax data store.  The residue will be added to the current data pipe.'
    title = 'Addition of new residues'


    def add_uf(self, sizer):
        """Add the residue specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Molecule and residue selections.
        self.mol = self.combo_box(sizer, "The molecule:", [])

        # The residue name input.
        self.res_name = self.input_field(sizer, "The name of the residue:")

        # The type selection.
        self.res_num = self.input_field(sizer, "The residue number:")


    def execute(self):
        """Execute the user function."""

        # The molecule name.
        mol_name = str(self.mol.GetValue())
        if mol_name == '':
            mol_name = None

        # The residue number.
        res_num = str(self.res_num.GetValue())
        if res_num == '':
            res_num = None
        else:
            res_num = int(res_num)

        # The residue name.
        res_name = str(self.res_name.GetValue())
        if res_num == '':
            res_num = None

        # Set the name.
        self.interpreter.residue.create(res_name=res_name, res_num=res_num, mol_name=mol_name)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.mol.Clear()

        # Clear the text.
        self.mol.SetValue('')

        # The list of molecule names.
        if pipes.cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)



class Delete_window(UF_window):
    """The residue.delete() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Delete a residue'
    image_path = WIZARD_IMAGE_PATH + 'residue.png'
    main_text = 'This dialog allows you to delete residues from the relax data store.  The residue will be deleted from the current data pipe.'
    title = 'Residue deletion'


    def add_uf(self, sizer):
        """Add the residue specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The residue selection.
        self.res_name = self.combo_box(sizer, "The residue:", [])


    def execute(self):
        """Execute the user function."""

        # Get the name.
        res_name = str(self.res_name.GetValue())

        # The residue ID.
        id = ':' + res_name

        # Delete the residue.
        self.interpreter.residue.delete(res_id=id)

        # Update.
        self.update(None)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.res_name.Clear()

        # Clear the residue name.
        self.res_name.SetValue('')

        # The list of residue names.
        if pipes.cdp_name():
            for res in res_loop():
                self.res_name.Append(res.name)
