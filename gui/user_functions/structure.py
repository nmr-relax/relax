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
import wx

# relax module imports.
from generic_fns.pipes import cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import float_to_gui, gui_to_bool, gui_to_float, gui_to_int, gui_to_str, str_to_gui
from gui.paths import WIZARD_IMAGE_PATH
from gui.wizard import Wiz_window


# The container class.
class Structure(UF_base):
    """The container class for holding all GUI elements."""

    def create_diff_tensor_pdb(self, event):
        """The structure.create_diff_tensor_pdb user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=900, size_y=800, title=self.get_title('structure', 'create_diff_tensor_pdb'))
        page = Create_diff_tensor_pdb_page(wizard, self.gui)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def create_vector_dist(self, event):
        """The structure.create_vector_dist user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=700, title=self.get_title('structure', 'create_vector_dist'))
        page = Create_vector_dist_page(wizard, self.gui)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def delete(self, event):
        """The structure.delete user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title=self.get_title('structure', 'delete'))
        page = Delete_page(wizard, self.gui)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def load_spins(self, event):
        """The structure.load_spins user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('structure', 'load_spins'))
        page = Load_spins_page(wizard, self.gui)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def read_pdb(self, event):
        """The structure.read_pdb user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('structure', 'read_pdb'))
        page = Read_pdb_page(wizard, self.gui)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def write_pdb(self, event):
        """The structure.write_pdb user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('structure', 'write_pdb'))
        page = Write_pdb_page(wizard, self.gui)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()


    def vectors(self, event):
        """The structure.vectors user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=600, title=self.get_title('structure', 'vectors'))
        page = Vectors_page(wizard, self.gui)
        wizard.add_page(page)

        # Execute the wizard.
        wizard.run()



class Create_diff_tensor_pdb_page(UF_page):
    """The structure.create_diff_tensor_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'create_diff_tensor_pdb.png'
    uf_path = ['structure', 'create_diff_tensor_pdb']
    height_desc = 400

    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The scale arg.
        self.scale = self.input_field(sizer, "Scaling factor:", tooltip=self.uf._doc_args_dict['scale'])
        self.scale.SetValue(float_to_gui(1.8e-6))

        # Add a file selection.
        self.file = self.file_selection(sizer, "The PDB file:", message="PDB file selection", wildcard="PDB files (*.pdb)|*.pdb;*.PDB", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "Force flag:", tooltip=self.uf._doc_args_dict['force'], default=False)


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())
        if not file:
            return

        # Force flag.
        force = gui_to_bool(self.force.GetValue())

        # The scaling.
        scale = gui_to_float(self.scale.GetValue())

        # Delete all structures.
        self.gui.interpreter.structure.create_diff_tensor_pdb(scale=scale, file=file, force=force)



class Create_vector_dist_page(UF_page):
    """The structure.create_vector_dist() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'create_vector_dist.png'
    uf_path = ['structure', 'create_vector_dist']

    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The length arg.
        self.length = self.input_field(sizer, "Vector length:", tooltip=self.uf._doc_args_dict['length'])
        self.length.SetValue(float_to_gui(2e-9))

        # Add a file selection.
        self.file = self.file_selection(sizer, "The PDB file:", message="PDB file selection", wildcard="PDB files (*.pdb)|*.pdb;*.PDB", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The symmetry flag.
        self.symmetry = self.boolean_selector(sizer, "Symmetry flag:", tooltip=self.uf._doc_args_dict['symmetry'], default=True)

        # The force flag.
        self.force = self.boolean_selector(sizer, "Force flag:", tooltip=self.uf._doc_args_dict['force'], default=False)


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())
        if not file:
            return

        # Force flag.
        force = gui_to_bool(self.force.GetValue())

        # The scaling.
        length = gui_to_float(self.length.GetValue())

        # Delete all structures.
        self.gui.interpreter.structure.create_vector_dist(length=length, file=file, symmetry=symmetry, force=force)



class Delete_page(UF_page):
    """The structure.delete() user function page."""

    # Some class variables.
    uf_path = ['structure', 'delete']

    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Delete all structures.
        self.gui.interpreter.structure.delete()



class Load_spins_page(UF_page):
    """The structure.load_spins() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'load_spins.png'
    uf_path = ['structure', 'load_spins']

    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The spin_id arg.
        self.spin_id = self.spin_id_element(sizer, default='@N')

        # The ave_pos arg.
        self.ave_pos = self.boolean_selector(sizer, "Average the atom position across models:", tooltip=self.uf._doc_args_dict['ave_pos'])
        self.ave_pos.SetValue(str_to_gui('True'))


    def on_execute(self):
        """Execute the user function."""

        # The args.
        spin_id = gui_to_str(self.spin_id.GetValue())
        ave_pos = gui_to_bool(self.ave_pos.GetValue())

        # Execute the user function.
        self.gui.interpreter.structure.load_spins(spin_id=spin_id, ave_pos=ave_pos)



class Read_pdb_page(UF_page):
    """The structure.read_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'read_pdb.png'
    uf_path = ['structure', 'read_pdb']

    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The PDB file:", message="PDB file selection", wildcard="PDB files (*.pdb)|*.pdb;*.PDB", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])

        # The read_mol arg.
        self.read_mol = self.input_field(sizer, "Read molecule number:", tooltip=self.uf._doc_args_dict['read_mol'])

        # The set_mol_name arg.
        self.set_mol_name = self.input_field(sizer, "Set the molecule name:", tooltip=self.uf._doc_args_dict['set_mol_name'])

        # The read_model arg.
        self.read_model = self.input_field(sizer, "Read model number:", tooltip=self.uf._doc_args_dict['read_model'])

        # The set_model_num arg.
        self.set_model_num = self.input_field(sizer, "Set the model number:", tooltip=self.uf._doc_args_dict['set_model_num'])

        # The PDB reader (default to internal).
        self.parser = self.combo_box(sizer, "The PDB parser:", choices=['internal', 'scientific'], tooltip=self.uf._doc_args_dict['parser'])
        self.parser.SetValue(str_to_gui('internal'))


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
        self.gui.interpreter.structure.read_pdb(file=file, read_mol=read_mol, set_mol_name=set_mol_name, read_model=read_model, set_model_num=set_model_num, parser=parser)



class Write_pdb_page(UF_page):
    """The structure.write_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'write_pdb.png'
    uf_path = ['structure', 'write_pdb']

    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The PDB file:", message="PDB file selection", wildcard="PDB files (*.pdb)|*.pdb;*.PDB", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The model_num arg.
        self.model_num = self.input_field(sizer, "Only write model number:", tooltip=self.uf._doc_args_dict['model_num'])


    def on_execute(self):
        """Execute the user function."""

        # The args.
        file = gui_to_str(self.file.GetValue())
        model_num = gui_to_str(self.model_num.GetValue())

        # Execute the user function.
        self.gui.interpreter.structure.write_pdb(file=file, model_num=model_num)



class Vectors_page(UF_page):
    """The structure.vectors() user function page."""

    # Some class variables.
    uf_path = ['structure', 'vectors']

    def add_contents(self, sizer):
        """Add the structure specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The attached atom.
        self.attached = self.input_field(sizer, "The attached atom:", tooltip=self.uf._doc_args_dict['attached'])
        self.attached.SetValue(str_to_gui("H"))

        # The spin_id arg.
        self.spin_id = self.spin_id_element(sizer, desc='Restrict vector loading to the spins:')

        # The model.
        self.model = self.input_field(sizer, "The model:", tooltip=self.uf._doc_args_dict['model'])

        # The verbosity level.
        self.verbosity = self.spin_control(sizer, "The verbosity level:", default=1, min=0, tooltip=self.uf._doc_args_dict['verbosity'])

        # The average.
        self.ave = self.boolean_selector(sizer, "Average the vector across models:", tooltip=self.uf._doc_args_dict['ave'])
        self.ave.SetValue(str_to_gui('True'))

        # The unit flag.
        self.unit = self.boolean_selector(sizer, "Calculate unit vectors:", tooltip=self.uf._doc_args_dict['unit'])
        self.unit.SetValue(str_to_gui('True'))


    def on_execute(self):
        """Execute the user function."""

        # The args.
        attached =  gui_to_str(self.attached.GetValue())
        spin_id =   gui_to_str(self.spin_id.GetValue())
        model =     gui_to_int(self.model.GetValue())
        verbosity = gui_to_int(self.verbosity.GetValue())
        ave =       gui_to_bool(self.ave.GetValue())
        unit =      gui_to_bool(self.unit.GetValue())

        # Execute the user function.
        self.gui.interpreter.structure.vectors(attached=attached, spin_id=spin_id, model=model, verbosity=verbosity, ave=ave, unit=unit)
