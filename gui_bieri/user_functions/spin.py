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
from gui_bieri.user_functions.mol_res_spin import Mol_res_spin


# The container class.
class Spin(UF_base):
    """The container class for holding all GUI elements."""

    def create(self, event, mol_name=None, res_num=None, res_name=None):
        """The spin.create user function.

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
        self._create_window = Create_window(self.gui, self.interpreter)

        # Default molecule name.
        if mol_name:
            self._create_window.mol.SetValue(mol_name)

        # Default residue.
        if res_num or res_name:
            self._create_window.res.SetValue("%s %s" % (res_num, res_name))

        # Show the dialog.
        self._create_window.ShowModal()

        # Destroy.
        self._create_window.Destroy()


    def delete(self, event, mol_name=None, res_num=None, res_name=None, spin_num=None, spin_name=None):
        """The spin.delete user function.

        @param event:       The wx event.
        @type event:        wx event
        @param mol_name:    The starting molecule name.
        @type mol_name:     str
        @param res_num:     The starting residue number.
        @type res_num:      str
        @param res_name:    The starting residue name.
        @type res_name:     str
        @param spin_num:    The starting spin number.
        @type spin_num:     str
        @param spin_name:   The starting spin name.
        @type spin_name:    str
        """

        # Initialise the dialog.
        self._delete_window = Delete_window(self.gui, self.interpreter)

        # Default molecule name.
        if mol_name:
            self._delete_window.mol.SetValue(mol_name)

        # Default residue.
        if res_num or res_name:
            self._delete_window.res.SetValue("%s %s" % (res_num, res_name))

        # Default spin.
        if spin_num or spin_name:
            self._delete_window.spin.SetValue("%s %s" % (spin_num, spin_name))

        # Show the dialog.
        self._delete_window.ShowModal()

        # Destroy.
        self._delete_window.Destroy()



class Create_window(UF_window, Mol_res_spin):
    """The spin.create() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Add a spin'
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'This dialog allows you to add new spins to the relax data store.  The spin will be added to the current data pipe.'
    title = 'Addition of new spins'

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

        # Get the molecule info.
        mol_name = str(self.mol.GetValue())
        if mol_name == '':
            mol_name = None

        # The residue info.
        res_num, res_name = self._get_res_info()

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

        # The list of molecule names.
        if pipes.cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)



class Delete_window(UF_window, Mol_res_spin):
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

        # Molecule, residue and spin selections.
        self.mol = self.combo_box(sizer, "The molecule:", [], self._update_residues)
        self.res = self.combo_box(sizer, "The residue:", [], self._update_spins)
        self.spin = self.combo_box(sizer, "The spin:", [])


    def execute(self):
        """Execute the user function."""

        # Get the spin ID.
        id = self._get_spin_id()

        # Nothing to do.
        if not id:
            return

        # Delete the spin.
        self.interpreter.spin.delete(spin_id=id)

        # Update the spin list.
        self._update_spins(None)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.mol.Clear()
        self.res.Clear()
        self.spin.Clear()

        # The list of molecule names.
        if pipes.cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)
