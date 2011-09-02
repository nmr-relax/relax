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
        wizard = Wiz_window(size_x=700, size_y=500, title=self.get_title('molecule', 'copy'))
        page = Copy_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def create(self, event):
        """The molecule.create user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=400, title=self.get_title('molecule', 'create'))
        page = Create_page(wizard, self.gui)
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
        wizard = Wiz_window(size_x=700, size_y=400, title=self.get_title('molecule', 'delete'))
        page = Delete_page(wizard, self.gui)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(str_to_gui(mol_name))

        # Execute the wizard.
        wizard.run()



class Copy_page(UF_page):
    """The molecule.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    uf_path = ['molecule', 'copy']

    def add_contents(self, sizer):
        """Add the molecule specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "The source data pipe:", [], evt_fn=self.update_mol_list, tooltip=self.uf._doc_args_dict['pipe_from'])

        # The molecule selection.
        self.mol_from = self.combo_box(sizer, "The source molecule:", [], tooltip=self.uf._doc_args_dict['mol_from'])

        # The destination pipe.
        self.pipe_to = self.combo_box(sizer, "The destination data pipe name:", [], tooltip=self.uf._doc_args_dict['pipe_to'])

        # The new molecule name.
        self.mol_to = self.input_field(sizer, "The new molecule name:", tooltip=self.uf._doc_args_dict['mol_to'])


    def on_display(self):
        """Update the pipe name lists."""

        # Set the default pipe name.
        if not gui_to_str(self.pipe_from.GetValue()):
            self.pipe_from.SetValue(str_to_gui(cdp_name()))
        if not gui_to_str(self.pipe_to.GetValue()):
            self.pipe_to.SetValue(str_to_gui(cdp_name()))

        # Clear the previous data.
        self.pipe_from.Clear()
        self.pipe_to.Clear()

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_from.Append(str_to_gui(name))
            self.pipe_to.Append(str_to_gui(name))

        # Update the molecule list.
        self.update_mol_list()


    def on_execute(self):
        """Execute the user function."""

        # Get the pipe names.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        pipe_to = gui_to_str(self.pipe_to.GetValue())

        # The molecule names.
        mol_from = gui_to_str(self.mol_from.GetValue())
        if mol_from:
            mol_from = "#" + mol_from
        mol_to = gui_to_str(self.mol_to.GetValue())
        if mol_to:
            mol_to = "#" + mol_to

        # Copy the molecule.
        self.gui.interpreter.queue('molecule.copy', pipe_from=pipe_from, mol_from=mol_from, pipe_to=pipe_to, mol_to=mol_to)


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



class Create_page(UF_page):
    """The molecule.create() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    uf_path = ['molecule', 'create']


    def add_contents(self, sizer):
        """Add the molecule specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The molecule name input.
        self.mol_name = self.input_field(sizer, "Molecule name:", tooltip=self.uf._doc_args_dict['mol_name'])

        # The type selection.
        self.mol_type = self.combo_box(sizer, "Molecule type:", ALLOWED_MOL_TYPES, tooltip=self.uf._doc_args_dict['mol_type'])


    def on_execute(self):
        """Execute the user function."""

        # Get the name and type.
        mol_name = str(self.mol_name.GetValue())
        mol_type = str(self.mol_type.GetValue())

        # Set the name.
        self.gui.interpreter.queue('molecule.create', mol_name=mol_name, mol_type=mol_type)



class Delete_page(UF_page):
    """The molecule.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    uf_path = ['molecule', 'delete']


    def add_contents(self, sizer):
        """Add the molecule specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The molecule selection.
        self.mol_id = self.combo_box(sizer, "Molecule ID:", [], tooltip=self.uf._doc_args_dict['mol_id'])


    def on_display(self):
        """Clear and update the molecule list."""

        # Clear the previous data.
        self.mol_id.Clear()

        # The list of molecule names.
        if cdp_name():
            for mol, mol_id in molecule_loop(return_id=True):
                self.mol_id.Append(str_to_gui(mol_id))


    def on_execute(self):
        """Execute the user function."""

        # Get the name.
        mol_id = gui_to_str(self.mol_id.GetValue())

        # Delete the molecule.
        self.gui.interpreter.queue('molecule.delete', mol_id=mol_id)
