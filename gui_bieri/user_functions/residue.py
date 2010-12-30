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
from generic_fns.mol_res_spin import generate_spin_id, molecule_loop, residue_loop
from generic_fns import pipes

# GUI module imports.
from base import UF_base, UF_window
from gui_bieri.paths import WIZARD_IMAGE_PATH
from gui_bieri.user_functions.mol_res_spin import Mol_res_spin


# The container class.
class Residue(UF_base):
    """The container class for holding all GUI elements."""

    def create(self, event, mol_name=None):
        """The residue.create user function.

        @param event:       The wx event.
        @type event:        wx event
        @param mol_name:    The starting molecule name.
        @type mol_name:     str
        """

        # Initialise the dialog.
        self._create_window = Create_window(self.gui, self.interpreter)

        # Default molecule name.
        if mol_name:
            self._create_window.mol.SetValue(mol_name)

        # Show the dialog.
        self._create_window.ShowModal()

        # Destroy.
        self._create_window.Destroy()


    def delete(self, event, mol_name=None, res_num=None, res_name=None):
        """The residue.delete user function.

        @param event:       The wx event.
        @type event:        wx event
        @param mol_name:    The starting molecule name.
        @type mol_name:     str
        @param res_num:     The starting residue number.
        @type res_num:      str
        @param res_name:    The starting residue name.
        @type res_name:     str
        """

        # Initialise the dialog.
        self._delete_window = Delete_window(self.gui, self.interpreter)

        # Default molecule name.
        if mol_name:
            self._delete_window.mol.SetValue(mol_name)

        # Default residue.
        if res_num or res_name:
            self._delete_window.res.SetValue("%s %s" % (res_num, res_name))

        # Show the dialog.
        self._delete_window.ShowModal()

        # Destroy.
        self._delete_window.Destroy()



class Create_window(UF_window, Mol_res_spin):
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

        # The list of molecule names.
        if pipes.cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)



class Delete_window(UF_window, Mol_res_spin):
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
        self.mol = self.combo_box(sizer, "The molecule:", [], self._update_residues)
        self.res = self.combo_box(sizer, "The residue:", [])


    def execute(self):
        """Execute the user function."""

        # The residue ID.
        id = self._get_res_id()

        # Nothing to do.
        if not id:
            return

        # Delete the residue.
        self.interpreter.residue.delete(res_id=id)

        # Update.
        self._update_residues(None)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.mol.Clear()
        self.res.Clear()

        # The list of molecule names.
        if pipes.cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)
