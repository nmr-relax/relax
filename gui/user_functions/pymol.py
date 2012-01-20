###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""The pymol user function GUI elements."""

# Python module imports.
from os import sep
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_bool, gui_to_float, gui_to_int, gui_to_str, str_to_gui


# The container class.
class Pymol(UF_base):
    """The container class for holding all GUI elements."""

    def clear_history(self):
        """The pymol.clear_history user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=600, size_y=300, name='pymol.clear_history', uf_page=Clear_history_page, apply_button=False)
        wizard.run()


    def command(self):
        """The pymol.command user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=700, size_y=400, name='pymol.command', uf_page=Command_page)
        wizard.run()


    def macro_apply(self):
        """The pymol.macro_apply user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=1000, size_y=750, name='pymol.macro_apply', uf_page=Macro_apply_page)
        wizard.run()


    def macro_run(self, file=None):
        """The pymol.macro_run user function.

        @keyword file:      The macro file to start the user function with.
        @type file:         str
        """

        # Create the wizard.
        wizard, page = self.create_wizard(size_x=800, size_y=400, name='pymol.macro_run', uf_page=Macro_run_page, return_page=True)

        # Default file name.
        if file:
            page.file.SetValue(str_to_gui(file))

        # Execute the wizard.
        wizard.run()


    def macro_write(self):
        """The pymol.macro_write user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=1000, size_y=750, name='pymol.macro_write', uf_page=Macro_write_page)
        wizard.run()


    def ribbon(self):
        """The pymol.ribbon user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=700, size_y=400, name='pymol.ribbon', uf_page=Ribbon_page, apply_button=False)
        wizard.run()


    def tensor_pdb(self):
        """The pymol.tensor_pdb user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=1000, size_y=700, name='pymol.tensor_pdb', uf_page=Tensor_pdb_page, apply_button=False)
        wizard.run()


    def view(self):
        """The pymol.view user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=600, size_y=300, name='pymol.view', uf_page=View_page, apply_button=False)
        wizard.run()



class Clear_history_page(UF_page):
    """The pymol.clear_history() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'clear_history']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Execute the user function.
        self.execute('pymol.clear_history')



class Command_page(UF_page):
    """The pymol.command() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'command']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The command.
        self.command = self.input_field(sizer, "The PyMOL command:", tooltip=self.uf._doc_args_dict['command'])


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        command = gui_to_str(self.command.GetValue())

        # Execute the user function.
        self.execute('pymol.command', command=command)



class Macro_apply_page(UF_page):
    """The pymol.macro_apply() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'macro_apply']
    height_desc = 450

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The data type.
        self.data_type = self.combo_box(sizer, "The data type:", choices=['s2', 's2f', 's2s', 'amp_fast', 'amp_slow', 'te', 'tf', 'ts', 'time_fast', 'time_slow', 'rex'], tooltip=self.uf._doc_args_dict['data_type'])

        # The style.
        self.style = self.input_field(sizer, "The style:", tooltip=self.uf._doc_args_dict['style'])
        self.style.SetValue(str_to_gui("classic"))

        # The starting colour.
        self.colour_start = self.input_field(sizer, "The starting colour:", tooltip=self.uf._doc_args_dict['colour_start'])

        # The ending colour.
        self.colour_end = self.input_field(sizer, "The ending colour:", tooltip=self.uf._doc_args_dict['colour_end'])

        # The colour list.
        self.colour_list = self.input_field(sizer, "The colour list:", tooltip=self.uf._doc_args_dict['colour_list'])


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        data_type = gui_to_str(self.data_type.GetValue())
        style = gui_to_str(self.style.GetValue())
        colour_start = gui_to_str(self.colour_start.GetValue())
        colour_end = gui_to_str(self.colour_end.GetValue())
        colour_list = gui_to_str(self.colour_list.GetValue())

        # Execute the user function.
        self.execute('pymol.macro_apply', data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)



class Ribbon_page(UF_page):
    """The pymol.ribbon() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'ribbon']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Execute the user function.
        self.execute('pymol.ribbon')



class Macro_run_page(UF_page):
    """The pymol.macro_run() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'macro_run']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The macro file:", message="PyMOL macro file selection", wildcard="PyMOL macro files (*.pml)|*.pml;*.PML", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())
        if not file:
            return

        # Execute the user function.
        self.execute('pymol.macro_run', file=file, dir=None)



class Macro_write_page(UF_page):
    """The pymol.macro_write() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'macro_write']
    height_desc = 400

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The macro file:", message="PyMOL macro file selection", wildcard="PyMOL macro files (*.pml)|*.pml;*.PML", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "Force flag:", tooltip=self.uf._doc_args_dict['force'], default=True)

        # The data type.
        self.data_type = self.combo_box(sizer, "The data type:", choices=['s2', 's2f', 's2s', 'amp_fast', 'amp_slow', 'te', 'tf', 'ts', ' time_fast', 'time_slow', 'rex'], tooltip=self.uf._doc_args_dict['data_type'])

        # The style.
        self.style = self.input_field(sizer, "The style:", tooltip=self.uf._doc_args_dict['style'])
        self.style.SetValue(str_to_gui("classic"))

        # The starting colour.
        self.colour_start = self.input_field(sizer, "The starting colour:", tooltip=self.uf._doc_args_dict['colour_start'])

        # The ending colour.
        self.colour_end = self.input_field(sizer, "The ending colour:", tooltip=self.uf._doc_args_dict['colour_end'])

        # The colour list.
        self.colour_list = self.input_field(sizer, "The colour list:", tooltip=self.uf._doc_args_dict['colour_list'])


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # Force flag.
        force = gui_to_bool(self.force.GetValue())

        # Get the values.
        data_type = gui_to_str(self.data_type.GetValue())
        style = gui_to_str(self.style.GetValue())
        colour_start = gui_to_str(self.colour_start.GetValue())
        colour_end = gui_to_str(self.colour_end.GetValue())
        colour_list = gui_to_str(self.colour_list.GetValue())

        # Execute the user function.
        self.execute('pymol.macro_write', data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, file=file, dir=None, force=force)



class Tensor_pdb_page(UF_page):
    """The pymol.tensor_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'tensor_pdb']
    height_desc = 450

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The tensor PDB file:", message="Tensor PDB file selection", wildcard="PDB files (*.pdb)|*.pdb;*.PDB", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Execute the user function.
        self.execute('pymol.tensor_pdb', file=file)



class View_page(UF_page):
    """The pymol.view() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'view']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Execute the user function.
        self.execute('pymol.view')
