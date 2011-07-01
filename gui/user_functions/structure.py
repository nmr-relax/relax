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
from gui.misc import gui_to_str, str_to_gui
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



class Delete_page(UF_page):
    """The structure.delete() user function page."""

    # Some class variables.
    main_text = 'Delete all structural information from the current data pipe.'
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



class Read_pdb_page(UF_page):
    """The structure.read_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + sep + 'structure' + sep + 'read_pdb.png'
    main_text = """The reading of PDB files into relax is quite a flexible procedure allowing for both models, defined as an ensemble of the same molecule but with different atomic positions, and different molecules within the same model.  One of more molecules can exist in one or more models.  The flexibility allows PDB models to be converted into different molecules and different PDB files loaded as the same molecule but as different models.  This flexibility is controlled by the four keyword arguments 'read_mol', 'set_mol_name', 'read_model', and 'set_model_num'.

        A few different PDB parsers can be used to read the structural data.  The choice of which to use depends on whether your PDB file is supported by that reader.  These are selected by setting the 'parser' argument to one of:

            'scientific' - the Scientific Python PDB parser.
            'internal' - a lower quality and less reliable, although faster, PDB parser built into relax.

        In a PDB file, the models are specified by the MODEL PDB record.  All the supported PDB readers in relax recognise this.  The molecule level is quite different between the Scientific Python and internal readers.  For how Scientific Python defines molecules, please see its documentation.  The internal reader is far simpler as it defines molecules using the TER PDB record.  In both cases, the molecules will be numbered consecutively from 1.

        The 'set_mol_name' argument is used to name the molecules within the PDB (within one model).  If not set, then the molecules will be named after the file name, with the molecule number appended if more than one exists.

        Note that relax will complain if it cannot work out what to do."""
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
