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
"""The residue user function GUI elements."""

# Python module imports.
from string import split

# relax module imports.
from generic_fns.mol_res_spin import generate_spin_id, molecule_loop, residue_loop
from generic_fns.pipes import cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.user_functions.mol_res_spin import Mol_res_spin
from gui.wizard import Wiz_window


# The container class.
class Residue(UF_base):
    """The container class for holding all GUI elements."""

    def copy(self, event):
        """The residue.copy user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=600, title=self.get_title('residue', 'copy'))
        page = Copy_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def create(self, event, mol_name=None):
        """The residue.create user function.

        @param event:       The wx event.
        @type event:        wx event
        @param mol_name:    The starting molecule name.
        @type mol_name:     str
        """

        # Initialise the wizard.
        wizard = Wiz_window(size_x=700, size_y=500, title=self.get_title('residue', 'create'))
        page = Create_page(wizard, self.gui)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(str_to_gui(mol_name))

        # Execute the wizard.
        wizard.run()


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

        # Initialise the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title=self.get_title('residue', 'delete'))
        page = Delete_page(wizard, self.gui)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(str_to_gui(mol_name))

        # Default residue.
        if res_num or res_name:
            page.res.SetValue(str_to_gui("%s %s" % (res_num, res_name)))

        # Execute the wizard.
        wizard.run()



class Copy_page(UF_page, Mol_res_spin):
    """The residue.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'residue.png'
    uf_path = ['residue', 'copy']

    def add_contents(self, sizer):
        """Add the residue specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "The source data pipe:", evt_fn=self.update_mol_list, tooltip=self.uf._doc_args_dict['pipe_from'])

        # The molecule selection.
        self.mol_from = self.combo_box(sizer, "The source molecule:", evt_fn=self.update_res_list)

        # The residue selection.
        self.res_from = self.combo_box(sizer, "The source residue:")

        # The destination pipe.
        self.pipe_to = self.combo_box(sizer, "The destination data pipe name:", tooltip=self.uf._doc_args_dict['pipe_to'], evt_fn=self.update_mol_list)

        # The destination molecule name.
        self.mol_to = self.combo_box(sizer, "The destination molecule name:")

        # The new residue number.
        self.res_num_to = self.input_field(sizer, "The new residue number:", tooltip='If left blank, the new residue will have the same number as the old.')

        # The new residue name.
        self.res_name_to = self.input_field(sizer, "The new residue name:", tooltip='If left blank, the new residue will have the same name as the old.')


    def on_display(self):
        """Update the pipe name lists."""

        # Set the default pipe name.
        if not gui_to_str(self.pipe_from.GetValue()):
            self.pipe_from.SetValue(str_to_gui(cdp_name()))
        if not gui_to_str(self.pipe_to.GetValue()):
            self.pipe_to.SetValue(str_to_gui(cdp_name()))

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

        # The residue names.
        res_from = self._get_res_id(suffix='_from')
        res_to = self._get_res_id(suffix='_to')
        if res_to == '':
            res_to = None

        # Copy the molecule.
        self.gui.interpreter.queue('residue.copy', pipe_from=pipe_from, res_from=res_from, pipe_to=pipe_to, res_to=res_to)


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
        """Update the list of molecules.

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



class Create_page(UF_page, Mol_res_spin):
    """The residue.create() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'residue.png'
    uf_path = ['residue', 'create']

    def add_contents(self, sizer):
        """Add the residue specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Molecule and residue selections.
        self.mol_name = self.combo_box(sizer, "The molecule:", [], tooltip=self.uf._doc_args_dict['mol_name'])

        # The residue name input.
        self.res_name = self.input_field(sizer, "The name of the residue:", tooltip=self.uf._doc_args_dict['res_name'])

        # The type selection.
        self.res_num = self.input_field(sizer, "The residue number:", tooltip=self.uf._doc_args_dict['res_num'])


    def on_display(self):
        """Update the molecule list."""

        # Clear the previous data.
        self.mol_name.Clear()

        # The list of molecule names.
        if cdp_name():
            for mol in molecule_loop():
                self.mol_name.Append(str_to_gui(mol.name))


    def on_execute(self):
        """Execute the user function."""

        # The molecule name.
        mol_name = str(self.mol_name.GetValue())
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
        self.gui.interpreter.queue('residue.create', res_name=res_name, res_num=res_num, mol_name=mol_name)



class Delete_page(UF_page, Mol_res_spin):
    """The residue.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'residue.png'
    uf_path = ['residue', 'delete']

    def add_contents(self, sizer):
        """Add the residue specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The residue selection.
        self.mol = self.combo_box(sizer, "The molecule:", [], self._update_residues)
        self.res = self.combo_box(sizer, "The residue:", [])


    def on_display(self):
        """Clear and update the residue and molecule lists."""

        # Clear the previous data.
        self.mol.Clear()
        self.res.Clear()

        # The list of molecule names.
        if cdp_name():
            for mol in molecule_loop():
                self.mol.Append(str_to_gui(mol.name))


    def on_execute(self):
        """Execute the user function."""

        # The residue ID.
        id = self._get_res_id()

        # Nothing to do.
        if not id:
            return

        # Delete the residue.
        self.gui.interpreter.queue('residue.delete', res_id=id)

        # Update.
        self._update_residues(None)
