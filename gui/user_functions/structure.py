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
"""The structure user function GUI elements."""

# Python module imports.
from os import sep
from string import split

# relax module imports.
from generic_fns.pipes import cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import gui_to_bool, gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.wizard import Wiz_window


# The container class.
class Structure(UF_base):
    """The container class for holding all GUI elements."""

    def delete(self, event):
        """The structure.delete user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Delete all structural data')
        page = Delete_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def load_spins(self, event):
        """The structure.load_spins user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title='Spin loader')
        page = Load_spins_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def read_pdb(self, event):
        """The structure.read_pdb user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title='PDB reader')
        page = Read_pdb_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def write_pdb(self, event):
        """The structure.write_pdb user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title='PDB writer')
        page = Write_pdb_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()



class Delete_page(UF_page):
    """The structure.delete() user function page."""

    # Some class variables.
    uf_path = ['structure', 'delete']
    title = 'Structure deletion'


    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Delete all structures.
        self.interpreter.structure.delete()



class Load_spins_page(UF_page):
    """The structure.load_spins() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'load_spins.png'
    uf_path = ['structure', 'load_spins']
    title = 'Load spins from structure'


    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin_id arg.
        self.spin_id = self.spin_id_element(sizer)

        # The combine_model arg.
        self.combine_model = self.combo_box(sizer, "Combine spins of all models:", choices=['True', 'False'], tooltip="The 'combine_models' user function argument:  A flag which specifies if spins from separate models should be combined.")
        self.combine_model.SetValue('True')

        # The ave_pos arg.
        self.ave_pos = self.combo_box(sizer, "Average the atom position across models:", choices=['True', 'False'], tooltip="The 'ave_pos' user function argument:  A flag specifying if the position of the atom is to be averaged across models.")
        self.ave_pos.SetValue('True')


    def on_execute(self):
        """Execute the user function."""

        # The args.
        spin_id = gui_to_str(self.spin_id.GetValue())
        combine_model = gui_to_bool(self.combine_model.GetValue())
        ave_pos = gui_to_bool(self.ave_pos.GetValue())

        # Execute the user function.
        self.interpreter.structure.load_spins(spin_id=spin_id, combine_model=combine_model, ave_pos=ave_pos)



class Read_pdb_page(UF_page):
    """The structure.read_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'read_pdb.png'
    uf_path = ['structure', 'read_pdb']
    title = 'PDB loading'


    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The PDB file:", title="PDB file selection")

        # The read_mol arg.
        self.read_mol = self.input_field(sizer, "Read molecule number:", tooltip="This is the 'read_mol' user function argument.")

        # The set_mol_name arg.
        self.set_mol_name = self.input_field(sizer, "Set the molecule name:", tooltip="This is the 'set_mol_name' user function argument.")

        # The read_model arg.
        self.read_model = self.input_field(sizer, "Read model number:", tooltip="This is the 'read_model' user function argument.")

        # The set_model_num arg.
        self.set_model_num = self.input_field(sizer, "Set the model number:", tooltip="This is the 'set_model_num' user function argument.")

        # The PDB reader (default to internal).
        self.parser = self.combo_box(sizer, "The PDB parser:", choices=['internal', 'scientific'], tooltip="This is the 'parser' user function argument.")
        self.parser.SetValue('internal')


    def on_execute(self):
        """Execute the user function."""

        # The args.
        file = gui_to_str(self.file.GetValue())
        read_mol = gui_to_str(self.read_mol.GetValue())
        set_mol_name = gui_to_str(self.set_mol_name.GetValue())
        read_model = gui_to_str(self.read_model.GetValue())
        set_model_num = gui_to_str(self.set_model_num.GetValue())
        parser = gui_to_str(self.parser.GetValue())

        # Execute the user function.
        self.interpreter.structure.read_pdb(file=file, read_mol=read_mol, set_mol_name=set_mol_name, read_model=read_model, set_model_num=set_model_num, parser=parser)



class Write_pdb_page(UF_page):
    """The structure.write_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'write_pdb.png'
    uf_path = ['structure', 'write_pdb']
    title = 'PDB writing'


    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The PDB file:", title="PDB file selection")

        # The model_num arg.
        self.model_num = self.input_field(sizer, "Only write model number:", tooltip="This is the 'model_num' user function argument.")


    def on_execute(self):
        """Execute the user function."""

        # The args.
        file = gui_to_str(self.file.GetValue())
        model_num = gui_to_str(self.model_num.GetValue())

        # Execute the user function.
        self.interpreter.structure.write_pdb(file=file, model_num=model_num)
