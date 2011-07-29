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
"""The sequence user function GUI elements."""

# Python module imports.
from string import split
import wx

# relax module imports.
from generic_fns.pipes import cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_bool, gui_to_int, gui_to_str, str_to_gui
from gui.wizard import Wiz_window


# The container class.
class Sequence(UF_base):
    """The container class for holding all GUI elements."""

    def copy(self, event):
        """The sequence.copy user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=500, title=self.get_title('sequence', 'copy'))
        page = Copy_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def read(self, event):
        """The sequence.read user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=900, size_y=700, title=self.get_title('sequence', 'read'))
        page = Read_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def write(self, event):
        """The sequence.write user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=900, size_y=700, title=self.get_title('sequence', 'write'))
        page = Write_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()



class Copy_page(UF_page):
    """The sequence.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'sequence.png'
    uf_path = ['sequence', 'copy']

    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "The source data pipe:", [], tooltip=self.uf._doc_args_dict['pipe_from'])

        # The destination pipe.
        self.pipe_to = self.combo_box(sizer, "The destination data pipe name:", [], tooltip=self.uf._doc_args_dict['pipe_to'])


    def on_display(self):
        """Update the pipe name lists."""

        # Set the default pipe name.
        if not gui_to_str(self.pipe_from.GetValue()):
            self.pipe_from.SetValue(str_to_gui(cdp_name()))
        if not gui_to_str(self.pipe_to.GetValue()):
            self.pipe_to.SetValue(str_to_gui(cdp_name()))

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_from.Append(name)
            self.pipe_to.Append(name)


    def on_execute(self):
        """Execute the user function."""

        # Get the pipe names.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        pipe_to = gui_to_str(self.pipe_to.GetValue())

        # Copy the sequence.
        self.gui.interpreter.sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to)



class Read_page(UF_page):
    """The sequence.read() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'sequence.png'
    uf_path = ['sequence', 'read']


    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The sequence file:", message="Sequence file selection", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])

        # The spin ID restriction.
        self.spin_id = self.spin_id_element(sizer, "Restrict data loading to certain spins:")

        # The parameter file settings.
        self.free_file_format(sizer)


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Get the column numbers.
        spin_id_col =   gui_to_int(self.spin_id_col.GetValue())
        mol_name_col =  gui_to_int(self.mol_name_col.GetValue())
        res_num_col =   gui_to_int(self.res_num_col.GetValue())
        res_name_col =  gui_to_int(self.res_name_col.GetValue())
        spin_num_col =  gui_to_int(self.spin_num_col.GetValue())
        spin_name_col = gui_to_int(self.spin_name_col.GetValue())

        # The column separator.
        sep = str(self.sep.GetValue())
        if sep == 'white space':
            sep = None

        # The spin ID.
        spin_id = gui_to_str(self.spin_id.GetValue())

        # Read the sequence.
        self.gui.interpreter.sequence.read(file=file, spin_id_col=spin_id_col, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, sep=sep, spin_id=spin_id)



class Write_page(UF_page):
    """The sequence.write() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'sequence.png'
    uf_path = ['sequence', 'write']


    def add_contents(self, sizer):
        """Add the sequence specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The sequence file:", message="Sequence file selection", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The column separator.
        self.sep = self.combo_box(sizer, "Column separator:", ["white space", ",", ";", ":", ""], tooltip=self.uf._doc_args_dict['sep'], read_only=False)
        self.sep.SetValue("white space")

        # The column flags.
        self.mol_name_flag = self.boolean_selector(sizer, "Molecule name flag:", tooltip=self.uf._doc_args_dict['mol_name_flag'])
        self.res_num_flag = self.boolean_selector(sizer, "Residue number flag:", tooltip=self.uf._doc_args_dict['res_num_flag'])
        self.res_name_flag = self.boolean_selector(sizer, "Residue name flag:", tooltip=self.uf._doc_args_dict['res_name_flag'])
        self.spin_num_flag = self.boolean_selector(sizer, "Spin number flag:", tooltip=self.uf._doc_args_dict['spin_num_flag'])
        self.spin_name_flag = self.boolean_selector(sizer, "Spin name flag:", tooltip=self.uf._doc_args_dict['spin_name_flag'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "Force flag:", tooltip=self.uf._doc_args_dict['force'])


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # The column separator.
        sep = str(self.sep.GetValue())
        if sep == 'white space':
            sep = None

        # Get the column flags.
        mol_name_flag =  gui_to_bool(self.mol_name_flag.GetValue())
        res_num_flag =   gui_to_bool(self.res_num_flag.GetValue())
        res_name_flag =  gui_to_bool(self.res_name_flag.GetValue())
        spin_num_flag =  gui_to_bool(self.spin_num_flag.GetValue())
        spin_name_flag = gui_to_bool(self.spin_name_flag.GetValue())

        # Force flag.
        force = gui_to_bool(self.force.GetValue())

        # Read the sequence.
        self.gui.interpreter.sequence.write(file=file, sep=sep, mol_name_flag=mol_name_flag, res_num_flag=res_num_flag, res_name_flag=res_name_flag, spin_num_flag=spin_num_flag, spin_name_flag=spin_name_flag, force=force)



