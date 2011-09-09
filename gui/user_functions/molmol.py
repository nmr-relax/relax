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
"""The molmol user function GUI elements."""

# Python module imports.
from os import sep
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_bool, gui_to_float, gui_to_int, gui_to_str, str_to_gui
from gui.wizard import Wiz_window


# The container class.
class Molmol(UF_base):
    """The container class for holding all GUI elements."""

    def clear_history(self, event):
        """The molmol.clear_history user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=300, title=self.get_title('molmol', 'clear_history'))
        page = Clear_history_page(wizard)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def command(self, event):
        """The molmol.command user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=400, title=self.get_title('molmol', 'command'))
        page = Command_page(wizard)
        wizard.add_page(page)
        wizard.run()


    def macro_apply(self, event):
        """The molmol.macro_apply user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=750, title=self.get_title('molmol', 'macro_apply'))
        page = Macro_apply_page(wizard)
        wizard.add_page(page)
        wizard.run()


    def macro_run(self, event, file=None):
        """The molmol.macro_run user function.

        @param event:       The wx event.
        @type event:        wx event
        @keyword file:      The macro file to start the user function with.
        @type file:         str
        """

        # Create the wizard.
        wizard = Wiz_window(size_x=800, size_y=400, title=self.get_title('molmol', 'macro_run'))
        page = Macro_run_page(wizard)
        wizard.add_page(page)

        # Default file name.
        if file:
            page.file.SetValue(str_to_gui(file))

        # Execute the wizard.
        wizard.run()


    def macro_write(self, event):
        """The molmol.macro_write user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=750, title=self.get_title('molmol', 'macro_write'))
        page = Macro_write_page(wizard)
        wizard.add_page(page)
        wizard.run()


    def ribbon(self, event):
        """The molmol.ribbon user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=400, title=self.get_title('molmol', 'ribbon'))
        page = Ribbon_page(wizard)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def tensor_pdb(self, event):
        """The molmol.tensor_pdb user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=700, title=self.get_title('molmol', 'tensor_pdb'))
        page = Tensor_pdb_page(wizard)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def view(self, event):
        """The molmol.view user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=300, title=self.get_title('molmol', 'view'))
        page = View_page(wizard)
        wizard.add_page(page, apply_button=False)
        wizard.run()



class Clear_history_page(UF_page):
    """The molmol.clear_history() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'clear_history']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Execute the user function.
        interpreter.queue('molmol.clear_history')



class Command_page(UF_page):
    """The molmol.command() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'command']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The command.
        self.command = self.input_field(sizer, "The Molmol command:", tooltip=self.uf._doc_args_dict['command'])


    def on_execute(self):
        """Execute the user function."""

        # Get the values.
        command = gui_to_str(self.command.GetValue())

        # Execute the user function.
        interpreter.queue('molmol.command', command=command)



class Macro_apply_page(UF_page):
    """The molmol.macro_apply() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'macro_apply']
    height_desc = 450

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The data type.
        self.data_type = self.combo_box(sizer, "The data type:", choices=['S2', 'S2f', 'S2s', 'amp_fast', 'amp_slow', 'te', 'tf', 'ts', 'time_fast', 'time_slow', 'Rex'], tooltip=self.uf._doc_args_dict['data_type'])

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
        interpreter.queue('molmol.macro_apply', data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)



class Macro_run_page(UF_page):
    """The molmol.macro_run() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'macro_run']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The macro file:", message="Molmol macro file selection", wildcard="Molmol macro files (*.mac)|*.mac;*.MAC", style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())
        if not file:
            return

        # Execute the user function.
        interpreter.queue('molmol.macro_run', file=file, dir=None)



class Macro_write_page(UF_page):
    """The molmol.macro_write() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'macro_write']
    height_desc = 400

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The macro file:", message="Molmol macro file selection", wildcard="Molmol macro files (*.mac)|*.mac;*.MAC", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "Force flag:", tooltip=self.uf._doc_args_dict['force'], default=True)

        # The data type.
        self.data_type = self.combo_box(sizer, "The data type:", choices=['S2', 'S2f', 'S2s', 'amp_fast', 'amp_slow', 'te', 'tf', 'ts',' time_fast', 'time_slow', 'Rex'], tooltip=self.uf._doc_args_dict['data_type'])

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
        if not file:
            return

        # Force flag.
        force = gui_to_bool(self.force.GetValue())

        # Get the values.
        data_type = gui_to_str(self.data_type.GetValue())
        style = gui_to_str(self.style.GetValue())
        colour_start = gui_to_str(self.colour_start.GetValue())
        colour_end = gui_to_str(self.colour_end.GetValue())
        colour_list = gui_to_str(self.colour_list.GetValue())

        # Execute the user function.
        interpreter.queue('molmol.macro_write', data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, file=file, dir=None, force=force)



class Ribbon_page(UF_page):
    """The molmol.ribbon() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'ribbon']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Execute the user function.
        interpreter.queue('molmol.ribbon')



class Tensor_pdb_page(UF_page):
    """The molmol.tensor_pdb() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'tensor_pdb']
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
        interpreter.queue('molmol.tensor_pdb', file=file)



class View_page(UF_page):
    """The molmol.view() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'molmol' + sep + 'molmol_logo.png'
    uf_path = ['molmol', 'view']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Execute the user function.
        interpreter.queue('molmol.view')
