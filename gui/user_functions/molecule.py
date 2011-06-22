###############################################################################
#                                                                             #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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

# relax module imports.
from generic_fns.mol_res_spin import ALLOWED_MOL_TYPES, generate_spin_id, molecule_loop
from generic_fns.pipes import cdp_name, get_pipe, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_str, str_to_gui
from gui.wizard import Wiz_window


# The container class.
class Molecule(UF_base):
    """The container class for holding all GUI elements."""

    def copy(self, event):
        """The molecule.copy user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=400, title='Copy a molecule')
        page = Copy_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()


    def create(self, event):
        """The molecule.create user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Add a molecule')
        page = Add_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()


    def delete(self, event, mol_name=None):
        """The molecule.delete user function.

        @param event:   The wx event.
        @type event:    wx event
        @param mol_name:    The starting molecule name.
        @type mol_name:     str
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Delete a molecule')
        page = Delete_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(mol_name)

        # Execute the wizard.
        wizard.run()



class Add_page(UF_page):
    """The molecule.create() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    main_text = 'This dialog allows you to add new molecules to the relax data store.  The molecule will be added to the current data pipe.'
    title = 'Addition of new molecules'


    def add_contents(self, sizer):
        """Add the molecule specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The molecule name input.
        self.mol = self.input_field(sizer, "The name of the molecule:")

        # The type selection.
        self.mol_type = self.combo_box(sizer, "The type of molecule:", ALLOWED_MOL_TYPES)


    def execute(self):
        """Execute the user function."""

        # Get the name and type.
        mol_name = str(self.mol.GetValue())
        mol_type = str(self.mol_type.GetValue())

        # Set the name.
        self.interpreter.molecule.create(mol_name=mol_name, type=mol_type)



class Copy_page(UF_page):
    """The molecule.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    main_text = 'This dialog allows you to copy molecules.'
    title = 'Molecule copy'


    def add_contents(self, sizer):
        """Add the molecule specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "The source data pipe:", [], evt_fn=self.update_mol_list)

        # The molecule selection.
        self.mol_from = self.combo_box(sizer, "The source molecule:", [])

        # The destination pipe.
        self.pipe_to = self.combo_box(sizer, "The destination data pipe name:", [])

        # The new molecule name.
        self.mol_to = self.input_field(sizer, "The new molecule name:", tooltip='If left blank, the new molecule will have the same name as the old.')


    def execute(self):
        """Execute the user function."""

        # Get the pipe names.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        pipe_to = gui_to_str(self.pipe_to.GetValue())

        # The molecule names.
        mol_from = "#" + gui_to_str(self.mol_from.GetValue())
        mol_to = gui_to_str(self.mol_to.GetValue())
        if mol_to:
            mol_to = "#" + mol_to

        # Copy the molecule.
        self.interpreter.molecule.copy(pipe_from=pipe_from, mol_from=mol_from, pipe_to=pipe_to, mol_to=mol_to)

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

        # Clear the previous data.
        self.mol_from.Clear()

        # The list of molecule names.
        for mol in molecule_loop(pipe=pipe_from):
            self.mol_from.Append(str_to_gui(mol.name))



class Delete_page(UF_page):
    """The molecule.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    main_text = 'This dialog allows you to delete molecules from the relax data store.  The molecule will be deleted from the current data pipe.'
    title = 'Molecule deletion'


    def add_contents(self, sizer):
        """Add the molecule specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The molecule selection.
        self.mol = self.combo_box(sizer, "The molecule:", [])


    def execute(self):
        """Execute the user function."""

        # Get the name.
        mol_name = str(self.mol.GetValue())

        # The molecule ID.
        id = generate_spin_id(mol_name=mol_name)

        # Delete the molecule.
        self.interpreter.molecule.delete(mol_id=id)

        # Update.
        self.update(None)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.mol.Clear()

        # The list of molecule names.
        if cdp_name():
            for mol in molecule_loop():
                self.mol.Append(mol.name)
