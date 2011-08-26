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
"""The pymol user function GUI elements."""

# Python module imports.
from os import sep
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.paths import WIZARD_IMAGE_PATH
from gui.misc import gui_to_bool, gui_to_float, gui_to_int, gui_to_str, str_to_gui
from gui.wizard import Wiz_window


# The container class.
class Pymol(UF_base):
    """The container class for holding all GUI elements."""

    def clear_history(self, event):
        """The pymol.clear_history user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=300, title=self.get_title('pymol', 'clear_history'))
        page = Clear_history_page(wizard, self.gui)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def command(self, event):
        """The pymol.command user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=400, title=self.get_title('pymol', 'command'))
        page = Command_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def macro_exec(self, event):
        """The pymol.macro_exec user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=750, title=self.get_title('pymol', 'macro_exec'))
        page = Macro_exec_page(wizard, self.gui)
        wizard.add_page(page)
        wizard.run()


    def ribbon(self, event):
        """The pymol.ribbon user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=400, title=self.get_title('pymol', 'ribbon'))
        page = Ribbon_page(wizard, self.gui)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def tensor_pdb(self, event):
        """The pymol.tensor_pdb user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=700, title=self.get_title('pymol', 'tensor_pdb'))
        page = Tensor_pdb_page(wizard, self.gui)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def view(self, event):
        """The pymol.view user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=300, title=self.get_title('pymol', 'view'))
        page = View_page(wizard, self.gui)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def write(self, event):
        """The pymol.write user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=1000, size_y=750, title=self.get_title('pymol', 'write'))
        page = Write_page(wizard, self.gui)
        wizard.add_page(page)
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
        self.gui.interpreter.queue('pymol.clear_history')



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
        self.gui.interpreter.queue('pymol.command', command=command)



class Macro_exec_page(UF_page):
    """The pymol.macro_exec() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'macro_exec']
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
        self.gui.interpreter.queue('pymol.macro_exec', data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)



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
        self.gui.interpreter.queue('pymol.ribbon')



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
        self.gui.interpreter.queue('pymol.tensor_pdb', file=file)



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
        self.gui.interpreter.queue('pymol.view')



class Write_page(UF_page):
    """The pymol.write() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pymol' + sep + 'pymol.png'
    uf_path = ['pymol', 'write']
    height_desc = 400

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The macro file:", message="PyMOL macro file selection", wildcard="PyMOL macro files (*.mac)|*.mac;*.MAC", style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

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
        self.gui.interpreter.queue('pymol.write', data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list, file=file, dir=None, force=force)
