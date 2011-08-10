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
from gui.misc import gui_to_bool, gui_to_int, gui_to_list, gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.user_functions.mol_res_spin import Mol_res_spin
from gui.wizard import Wiz_window


# The container class.
class Spin(UF_base):
    """The container class for holding all GUI elements."""

    def copy(self, event):
        """The spin.copy user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=600, title=self.get_title('spin', 'copy'))
        page = Copy_page(wizard, self.gui)
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
        wizard = Wiz_window(size_x=600, size_y=400, title=self.get_title('spin', 'create'))
        page = Create_page(wizard, self.gui)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(str_to_gui(mol_name))

        # Default residue.
        if res_num or res_name:
            page.res.SetValue(str_to_gui("%s %s" % (res_num, res_name)))

        # Execute the wizard.
        wizard.run()


    def create_pseudo(self, event):
        """The spin.create_pseudo user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('spin', 'create_pseudo'))
        page = Create_pseudo_page(wizard, self.gui)
        wizard.add_page(page)
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
        wizard = Wiz_window(size_x=600, size_y=400, title=self.get_title('spin', 'delete'))
        page = Delete_page(wizard, self.gui)
        wizard.add_page(page)

        # Default molecule name.
        if mol_name:
            page.mol.SetValue(str_to_gui(mol_name))

        # Default residue.
        if res_num or res_name:
            page.res.SetValue(str_to_gui("%s %s" % (res_num, res_name)))

        # Default spin.
        if spin_num or spin_name:
            page.spin.SetValue(str_to_gui("%s %s" % (spin_num, spin_name)))

        # Execute the wizard.
        wizard.run()


    def display(self, event):
        """The spin.display user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('spin', 'display'))
        page = Display_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def element(self, event):
        """The spin.element user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('spin', 'element'))
        page = Element_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def name(self, event):
        """The spin.name user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('spin', 'name'))
        page = Name_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def number(self, event):
        """The spin.number user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('spin', 'number'))
        page = Number_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()



class Copy_page(UF_page, Mol_res_spin):
    """The spin.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    uf_path = ['spin', 'copy']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "The source data pipe:", tooltip=self.uf._doc_args_dict['pipe_from'], evt_fn=self.update_mol_list)

        # The molecule selection.
        self.mol_from = self.combo_box(sizer, "The source molecule:", evt_fn=self.update_res_list)

        # The residue selection.
        self.res_from = self.combo_box(sizer, "The source residue:", evt_fn=self.update_spin_list)

        # The spin selection.
        self.spin_from = self.combo_box(sizer, "The source spin:")

        # The destination pipe.
        self.pipe_to = self.combo_box(sizer, "The destination data pipe name:", tooltip=self.uf._doc_args_dict['pipe_to'], evt_fn=self.update_mol_list)

        # The destination molecule name.
        self.mol_to = self.combo_box(sizer, "The destination molecule name:")

        # The destination residue.
        self.res_num_to = self.input_field(sizer, "The new residue number:")
        self.res_name_to = self.input_field(sizer, "The new residue name:")

        # The destination spin.
        self.spin_num_to = self.input_field(sizer, "The new spin number:", tooltip='If left blank, the new spin will have the same number as the old.')
        self.spin_name_to = self.input_field(sizer, "The new spin name:", tooltip='If left blank, the new spin will have the same name as the old.')


    def on_display(self):
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
            self.pipe_from.Append(str_to_gui(name))
            self.pipe_to.Append(str_to_gui(name))

        # Update the molecule list.
        self.update_mol_list()


    def on_execute(self):
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
        self.gui.interpreter.queue('spin.copy', pipe_from=pipe_from, spin_from=spin_from, pipe_to=pipe_to, spin_to=spin_to)


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
    uf_path = ['spin', 'create']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Molecule and residue selections.
        self.mol = self.combo_box(sizer, "The molecule:", [], self._update_residues)
        self.res = self.combo_box(sizer, "The residue:", [])

        # The spin name input.
        self.spin_name = self.input_field(sizer, "The name of the spin:", tooltip=self.uf._doc_args_dict['spin_name'])

        # The type selection.
        self.spin_num = self.input_field(sizer, "The spin number:", tooltip=self.uf._doc_args_dict['spin_num'])


    def on_display(self):
        """Clear all data and then update the list of molecule names."""

        # Clear the previous data.
        self.mol.Clear()
        self.res.Clear()

        # The list of molecule names.
        if cdp_name():
            for mol in molecule_loop():
                self.mol.Append(str_to_gui(mol.name))


    def on_execute(self):
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
        self.gui.interpreter.queue('spin.create', spin_name=spin_name, spin_num=spin_num, res_name=res_name, res_num=res_num, mol_name=mol_name)



class Create_pseudo_page(UF_page, Mol_res_spin):
    """The spin.create_pseudo() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    uf_path = ['spin', 'create_pseudo']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The name and number of the spin.
        self.spin_name = self.input_field(sizer, "The pseudo-spin name:", tooltip=self.uf._doc_args_dict['spin_name'])
        self.spin_num = self.input_field(sizer, "The pseudo-spin number:", tooltip=self.uf._doc_args_dict['spin_num'])

        # The spin ID.
        self.res_id = self.spin_id_element(sizer, desc="The residue ID string:", choices=[])

        # The members.
        self.members = self.input_field(sizer, "The pseudo-spin members:", tooltip=self.uf._doc_args_dict['members'])

        # The pos averaging.
        self.averaging = self.combo_box(sizer, "The positional averaging:", tooltip=self.uf._doc_args_dict['averaging'], choices=['linear'])
        self.averaging.SetValue(str_to_gui('linear'))


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        spin_name = gui_to_str(self.spin_name.GetValue())
        spin_num = gui_to_int(self.spin_num.GetValue())
        res_id = gui_to_str(self.res_id.GetValue())
        members = gui_to_list(self.members.GetValue())
        averaging = gui_to_str(self.averaging.GetValue())

        # Execute.
        self.gui.interpreter.queue('spin.create_pseudo', spin_name=spin_name, spin_num=spin_num, res_id=res_id, members=members, averaging=averaging)



class Delete_page(UF_page, Mol_res_spin):
    """The spin.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    uf_path = ['spin', 'delete']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Molecule, residue and spin selections.
        self.mol = self.combo_box(sizer, "The molecule:", [], self._update_residues)
        self.res = self.combo_box(sizer, "The residue:", [], self._update_spins)
        self.spin = self.combo_box(sizer, "The spin:", [])


    def on_display(self):
        """Clear the spin data and update the mol list."""

        # Clear the previous data.
        self.mol.Clear()
        self.res.Clear()
        self.spin.Clear()

        # The list of molecule names.
        if cdp_name():
            for mol in molecule_loop():
                self.mol.Append(str_to_gui(mol.name))


    def on_execute(self):
        """Execute the user function."""

        # Get the spin ID.
        id = self._get_spin_id()

        # Nothing to do.
        if not id:
            return

        # Delete the spin.
        self.gui.interpreter.queue('spin.delete', spin_id=id)

        # Update the spin list.
        self._update_spins(None)



class Display_page(UF_page, Mol_res_spin):
    """The spin.display() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    uf_path = ['spin', 'display']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin ID.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict to the spin ID:")


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Execute.
        self.gui.interpreter.queue('spin.display', spin_id=spin_id)



class Element_page(UF_page, Mol_res_spin):
    """The spin.element() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    uf_path = ['spin', 'element']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin ID.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict the element setting to the spins:")

        # The element.
        self.element = self.combo_box(sizer, "The element:", tooltip=self.uf._doc_args_dict['element'], choices=['H', 'N', 'C','O', 'P'], read_only=False)

        # The force flag.
        self.force = self.boolean_selector(sizer, "The force flag:", tooltip=self.uf._doc_args_dict['force'], default=False)


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        spin_id = gui_to_str(self.spin_id.GetValue())
        element = gui_to_str(self.element.GetValue())
        force = gui_to_bool(self.force.GetValue())

        # Execute.
        self.gui.interpreter.queue('spin.element', spin_id=spin_id, element=element, force=force)



class Name_page(UF_page, Mol_res_spin):
    """The spin.name() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    uf_path = ['spin', 'name']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin ID.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict the naming to the spins:")

        # The name.
        self.name = self.input_field(sizer, "The name:", tooltip=self.uf._doc_args_dict['name'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "The force flag:", tooltip=self.uf._doc_args_dict['force'], default=False)


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        spin_id = gui_to_str(self.spin_id.GetValue())
        name = gui_to_str(self.name.GetValue())
        force = gui_to_bool(self.force.GetValue())

        # Execute.
        self.gui.interpreter.queue('spin.name', spin_id=spin_id, name=name, force=force)



class Number_page(UF_page, Mol_res_spin):
    """The spin.number() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'spin.png'
    uf_path = ['spin', 'number']

    def add_contents(self, sizer):
        """Add the page specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin ID.
        self.spin_id = self.spin_id_element(sizer, desc="Restrict the numbering to the spins:")

        # The number.
        self.number = self.input_field(sizer, "The number:", tooltip=self.uf._doc_args_dict['number'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "The force flag:", tooltip=self.uf._doc_args_dict['force'], default=False)


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        spin_id = gui_to_str(self.spin_id.GetValue())
        number = gui_to_int(self.number.GetValue())
        force = gui_to_bool(self.force.GetValue())

        # Execute.
        self.gui.interpreter.queue('spin.number', spin_id=spin_id, number=number, force=force)
