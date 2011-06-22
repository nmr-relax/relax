###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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

# relax module imports.
from generic_fns.mol_res_spin import generate_spin_id, molecule_loop, residue_loop, spin_loop
from generic_fns.pipes import cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.user_functions.mol_res_spin import Mol_res_spin
from gui.wizard import Wiz_window


# The container class.
class Spin(UF_base):
    """The container class for holding all GUI elements."""

    def copy(self, event):
        """The residue.copy user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=600, title='Copy a spin')
        page = Copy_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()


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

        # Create the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Add a spin')
        page = Create_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(mol_name)

        # Default residue.
        if res_num or res_name:
            page.res.SetValue("%s %s" % (res_num, res_name))

        # Execute the wizard.
        wizard.run()


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

        # Create the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Delete a spin')
        page = Delete_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(mol_name)

        # Default residue.
        if res_num or res_name:
            page.res.SetValue("%s %s" % (res_num, res_name))

        # Default spin.
        if spin_num or spin_name:
            page.spin.SetValue("%s %s" % (spin_num, spin_name))

        # Execute the wizard.
        wizard.run()



class Copy_page(UF_page, Mol_res_spin):
    """The spin.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'This dialog allows you to copy spin.'
    title = 'Spin copy'


    def add_contents(self, sizer):
        """Add the spin specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "The source data pipe:", evt_fn=self.update_mol_list)

        # The molecule selection.
        self.mol_from = self.combo_box(sizer, "The source molecule:", evt_fn=self.update_res_list)

        # The residue selection.
        self.res_from = self.combo_box(sizer, "The source residue:", evt_fn=self.update_spin_list)

        # The spin selection.
        self.spin_from = self.combo_box(sizer, "The source spin:")

        # The destination pipe.
        self.pipe_to = self.combo_box(sizer, "The destination data pipe name:", evt_fn=self.update_mol_list)

        # The destination molecule name.
        self.mol_to = self.combo_box(sizer, "The destination molecule name:")

        # The destination residue.
        self.res_to = self.combo_box(sizer, "The destination residue:")

        # The new spin number.
        self.spin_num_to = self.input_field(sizer, "The new spin number:", tooltip='If left blank, the new spin will have the same number as the old.')

        # The new spin name.
        self.spin_name_to = self.input_field(sizer, "The new spin name:", tooltip='If left blank, the new spin will have the same name as the old.')


    def execute(self):
        """Execute the user function."""

        # Get the pipe names.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        pipe_to = gui_to_str(self.pipe_to.GetValue())

        # The spin names.
        spin_from = self._get_spin_id(suffix='_from')
        spin_to = self._get_spin_id(suffix='_to')
        if spin_to == '':
            spin_to = None

        # Copy the spin.
        self.interpreter.spin.copy(pipe_from=pipe_from, spin_from=spin_from, pipe_to=pipe_to, spin_to=spin_to)

        # Update.
        self.update(None)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the default pipe name.
        if not gui_to_str(self.pipe_from.GetValue()):
            self.pipe_from.SetValue(str_to_gui(cdp_name()))
        if not gui_to_str(self.pipe_to.GetValue()):
            self.pipe_to.SetValue(str_to_gui(cdp_name()))

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_from.Append(name)
            self.pipe_to.Append(name)

        # Update the molecule list.
        self.update_mol_list()


    def update_mol_list(self, event=None):
        """Update the list of molecules.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The source data pipe.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        pipe_to = gui_to_str(self.pipe_to.GetValue())

        # Clear the previous data.
        self.mol_from.Clear()
        self.mol_to.Clear()

        # The list of molecule names.
        for mol in molecule_loop(pipe=pipe_from):
            self.mol_from.Append(str_to_gui(mol.name))
        for mol in molecule_loop(pipe=pipe_to):
            self.mol_to.Append(str_to_gui(mol.name))

        # Update the residues too.
        self.update_res_list()


    def update_res_list(self, event=None):
        """Update the list of residues.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The source data pipe and molecule name.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        mol_from = generate_spin_id(mol_name=gui_to_str(self.mol_from.GetValue()))

        # Clear the previous data.
        self.res_from.Clear()

        # Nothing to do.
        if mol_from == '':
            return

        # The list of molecule names.
        for res in residue_loop(mol_from, pipe=pipe_from):
            self.res_from.Append(str_to_gui("%s %s" % (res.num, res.name)))

        # Update the spins too.
        self.update_spin_list()


    def update_spin_list(self, event=None):
        """Update the list of spins.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The source data pipe and molecule name.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        res_from = self._get_res_id(suffix='_from')

        # Clear the previous data.
        self.spin_from.Clear()

        # Nothing to do.
        if res_from == '':
            return

        # The list of molecule names.
        for spin in spin_loop(res_from, pipe=pipe_from):
            self.spin_from.Append(str_to_gui("%s %s" % (spin.num, spin.name)))



class Create_page(UF_page, Mol_res_spin):
    """The spin.create() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'This dialog allows you to add new spins to the relax data store.  The spin will be added to the current data pipe.'
    title = 'Addition of new spins'

    def add_contents(self, sizer):
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
        if cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)



class Delete_page(UF_page, Mol_res_spin):
    """The spin.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    main_text = 'This dialog allows you to delete spins from the relax data store.  The spin will be deleted from the current data pipe.'
    title = 'Spin deletion'


    def add_contents(self, sizer):
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
        if cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)
