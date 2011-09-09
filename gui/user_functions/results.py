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
"""The results user function GUI elements."""

# Python module imports.
from os import sep
import wx

# GUI module imports.
from base import UF_base, UF_page
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import gui_to_bool, gui_to_float, gui_to_int, gui_to_str, int_to_gui, str_to_gui
from gui.wizard import Wiz_window


# The container class.
class Results(UF_base):
    """The container class for holding all GUI elements."""

    def display(self, event):
        """The results.display user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=300, title=self.get_title('results', 'display'))
        page = Display_page(wizard)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def read(self, event):
        """The results.read user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=700, size_y=500, title=self.get_title('results', 'read'))
        page = Read_page(wizard)
        wizard.add_page(page, apply_button=False)
        wizard.run()


    def write(self, event):
        """The results.write user function.

        @param event:       The wx event.
        @type event:        wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=900, size_y=700, title=self.get_title('results', 'write'))
        page = Write_page(wizard)
        wizard.add_page(page, apply_button=False)
        wizard.run()



class Display_page(UF_page):
    """The results.display() user function page."""

    # Some class variables.
    uf_path = ['results', 'display']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def on_execute(self):
        """Execute the user function."""

        # Execute the user function.
        interpreter.queue('results.display')



class Read_page(UF_page):
    """The results.read() user function page."""

    # Some class variables.
    uf_path = ['results', 'read']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The results file:", message="Results file selection", wildcard='relax results files (*.bz2)|*.bz2|relax results files (*.gz)|*.gz|relax results files (*.*)|*.*', style=wx.FD_OPEN, tooltip=self.uf._doc_args_dict['file'])


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetValue())

        # No file.
        if not file:
            return

        # Execute the user function.
        interpreter.queue('results.read', file=file)



class Write_page(UF_page):
    """The results.write() user function page."""

    # Some class variables.
    height_desc = 400
    uf_path = ['results', 'write']

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add a file selection.
        self.file = self.file_selection(sizer, "The results file:", message="Results file selection", wildcard='relax results files (*.bz2)|*.bz2|relax results files (*.gz)|*.gz|relax results files (*.*)|*.*', style=wx.FD_SAVE, tooltip=self.uf._doc_args_dict['file'])

        # The force flag.
        self.force = self.boolean_selector(sizer, "Force flag:", tooltip=self.uf._doc_args_dict['force'])

        # The compression type.
        self.compress_type = self.combo_box(sizer, "The compression type:", ["0:  No compression.", "1:  Bzip2 compression.", "2:  Gzip compression."], tooltip=self.uf._doc_args_dict['compress_type'], read_only=True)
        self.compress_type.SetSelection(1)


    def on_execute(self):
        """Execute the user function."""

        # The file name.
        file = gui_to_str(self.file.GetSelection())

        # No file.
        if not file:
            return

        # Get the values.
        compress_type = gui_to_int(self.compress_type.GetValue())
        force = gui_to_bool(self.force.GetValue())

        # Execute the user function.
        interpreter.queue('results.write', file=file, force=force, compress_type=compress_type)
