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
"""The spin user function GUI elements."""

# Python module imports.
from string import split
import wx

# relax module imports.
from generic_fns.mol_res_spin import molecule_loop, residue_loop, spin_loop
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_window
from gui_bieri.paths import WIZARD_IMAGE_PATH


# The container class.
class Spin(UF_base):
    """The container class for holding all GUI elements."""

    def setup(self):
        """Place all the GUI classes into this class for storage."""

        # The dialogs.
        self._create_window = Add_window(self.gui, self.interpreter)
        self._delete_window = Delete_window(self.gui, self.interpreter)


    def create(self, event):
        """The spin.create user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._create_window.Show()


    def delete(self, event):
        """The spin.delete user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._delete_window.Show()


    def destroy(self):
        """Close all windows."""

        self._create_window.Destroy()
        self._delete_window.Destroy()



class Add_window(UF_window):
    """The spin.create() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Add a spin'
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'This dialog allows you to add new spins to the relax data store.  The spin will be added to the current data pipe.'
    title = 'Addition of new spins'


    def _update_residues(self, event):
        """Update the residue combo box.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.res.Clear()

        # Clear the text.
        self.res.SetValue('')

        # The list of residue names.
        mol_id = '#' + str(self.mol.GetValue())
        for res in residue_loop(mol_id):
            self.res.Append("%s %s" % (res.num, res.name))


    def add_uf(self, sizer):
        """Add the spin specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Molecule and residue selections.
        self.mol = self.combo_box(sizer, "The molecule:", [], self._update_residues)
        self.res = self.combo_box(sizer, "The residue:", [])

        # The spin name input.
        self.spin_name = self.input_field(sizer, "The name of the spin:")

        # The type selection.
        self.spin_num = self.input_field(sizer, "The spin number:")


    def execute(self):
        """Execute the user function."""

        # Get the spin info.
        mol_name = str(self.mol.GetValue())
        if mol_name == '':
            mol_name = None

        # The residue info.
        res = str(self.res.GetValue())
        res_num, res_name = split(res)
        if res_name == '':
            res_name = None
        if res_num == '':
            res_num = None
        else:
            res_num = int(res_num)

        # The spin number.
        spin_num = str(self.spin_num.GetValue())
        if spin_num == '':
            spin_num = None
        else:
            spin_num = int(spin_num)

        # The spin name.
        spin_name = str(self.spin_name.GetValue())
        if spin_num == '':
            spin_num = None

        # Set the name.
        self.interpreter.spin.create(spin_name=spin_name, spin_num=spin_num, res_name=res_name, res_num=res_num, mol_name=mol_name)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.mol.Clear()
        self.res.Clear()

        # Clear the text.
        self.mol.SetValue('')
        self.res.SetValue('')

        # The list of molecule names.
        if pipes.cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)



class Delete_window(UF_window):
    """The spin.delete() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Delete a spin'
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'This dialog allows you to delete spins from the relax data store.  The spin will be deleted from the current data pipe.'
    title = 'Spin deletion'


    def add_uf(self, sizer):
        """Add the spin specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin selection.
        self.spin_name = self.combo_box(sizer, "The spin:", [])


    def execute(self):
        """Execute the user function."""

        # Get the name.
        spin_name = str(self.spin_name.GetValue())

        # The spin ID.
        id = '@' + spin_name

        # Delete the spin.
        self.interpreter.spin.delete(spin_id=id)

        # Update.
        self.update(None)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.spin_name.Clear()

        # Clear the spin name.
        self.spin_name.SetValue('')

        # The list of spin names.
        if pipes.cdp_name():
            for spin in spin_loop():
                self.spin_name.Append(spin.name)
