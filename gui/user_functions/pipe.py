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
"""The pipe user function GUI elements."""

# Python module imports.
import wx

# relax module imports.
from generic_fns.pipes import PIPE_DESC, VALID_TYPES, cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import gui_to_list, gui_to_str, str_to_gui
from gui.components.combo_list import Combo_list
from gui.paths import WIZARD_IMAGE_PATH


# The container class.
class Pipe(UF_base):
    """The container class for holding all GUI elements."""

    def copy(self):
        """The pipe.copy user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=600, size_y=400, name='pipe.copy', uf_page=Copy_page)
        wizard.run()


    def create(self):
        """The pipe.create user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=700, size_y=500, name='pipe.create', uf_page=Create_page)
        wizard.run()


    def delete(self):
        """The pipe.delete user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=600, size_y=400, name='pipe.delete', uf_page=Delete_page)
        wizard.run()


    def hybridise(self):
        """The pipe.hybridise user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=800, size_y=800, name='pipe.hybridise', uf_page=Hybridise_page)
        wizard.run()


    def switch(self):
        """The pipe.switch user function."""

        # Execute the wizard.
        wizard = self.create_wizard(size_x=650, size_y=450, name='pipe.switch', uf_page=Switch_page, apply_button=False)
        wizard.run()



class Copy_page(UF_page):
    """The pipe.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    uf_path = ['pipe', 'copy']

    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "Source pipe:", [], tooltip=self.uf._doc_args_dict['pipe_from'])

        # The destination pipe.
        self.pipe_to = self.input_field(sizer, "Destination pipe name:", tooltip=self.uf._doc_args_dict['pipe_to'])


    def on_display(self):
        """Clear the data is apply was hit."""

        # Clear the previous data.
        self.pipe_from.Clear()

        # Clear the pipe name.
        self.pipe_from.SetValue(str_to_gui(''))

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_from.Append(str_to_gui(name))


    def on_execute(self):
        """Execute the user function."""

        # Get the pipe names.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        pipe_to = gui_to_str(self.pipe_to.GetValue())

        # Copy the data pipe.
        self.execute('pipe.copy', pipe_from, pipe_to)



class Create_page(UF_page):
    """The pipe.create() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    uf_path = ['pipe', 'create']

    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe name input.
        self.pipe_name = self.input_field(sizer, "The data pipe name:", tooltip=self.uf._doc_args_dict['pipe_name'])

        # The type selection.
        self.pipe_type = self.combo_box(sizer, "The type of data pipe:", tooltip=self.uf._doc_args_dict['pipe_type'], read_only=True)
        for i in range(len(VALID_TYPES)):
            self.pipe_type.Append(PIPE_DESC[VALID_TYPES[i]])
            self.pipe_type.SetClientData(i, VALID_TYPES[i])


    def on_execute(self):
        """Execute the user function."""

        # Get the name and type.
        pipe_name = gui_to_str(self.pipe_name.GetValue())
        pipe_type = self.pipe_type.GetClientData(self.pipe_type.GetSelection())

        # Set the name.
        self.execute('pipe.create', pipe_name=pipe_name, pipe_type=pipe_type)



class Delete_page(UF_page):
    """The pipe.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    uf_path = ['pipe', 'delete']


    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe selection.
        self.pipe_name = self.combo_box(sizer, "The pipe:", [], tooltip=self.uf._doc_args_dict['pipe_name'])


    def on_display(self):
        """Clear and update the pipe name list."""

        # Clear the previous data.
        self.pipe_name.Clear()

        # Clear the pipe name.
        self.pipe_name.SetValue(str_to_gui(''))

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(str_to_gui(name))


    def on_execute(self):
        """Execute the user function."""

        # Get the name.
        pipe_name = str(self.pipe_name.GetValue())

        # Delete the data pipe.
        self.execute('pipe.delete', pipe_name)



class Hybridise_page(UF_page):
    """The pipe.hybridise() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe_hybrid.png'
    uf_path = ['pipe', 'hybridise']


    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The hybrid data pipe name input.
        self.hybrid = self.input_field(sizer, "The hybrid pipe name:", tooltip=self.uf._doc_args_dict['hybrid'])

        # The pipe selection.
        self.pipes = Combo_list(self, sizer, "The pipes to hybridise:", n=2, choices=pipe_names(), tooltip=self.uf._doc_args_dict['pipes'])


    def on_execute(self):
        """Execute the user function."""

        # Get the name.
        hybrid = gui_to_str(self.hybrid.GetValue())
        pipes = gui_to_list(self.pipes.GetValue())

        # Delete the data pipe.
        self.execute('pipe.hybridise', hybrid=hybrid, pipes=pipes)



class Switch_page(UF_page):
    """The pipe.switch() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe_switch.png'
    uf_path = ['pipe', 'switch']

    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The current data pipe.
        self.cdp = self.text(sizer, "The current data pipe (cdp):")

        # The pipe selection.
        self.pipe_name = self.combo_box(sizer, "The pipe:", [], tooltip=self.uf._doc_args_dict['pipe_name'])


    def on_display(self):
        """Clear and update the pipe name list and cdp."""

        # Clear the previous data.
        self.pipe_name.Clear()
        self.cdp.Clear()

        # Clear the pipe name.
        self.pipe_name.SetValue(str_to_gui(''))
        self.cdp.SetValue(str_to_gui(cdp_name()))

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(str_to_gui(name))


    def on_execute(self):
        """Execute the user function."""

        # Get the name.
        pipe_name = str(self.pipe_name.GetValue())

        # Switch the data pipe.
        self.execute('pipe.switch', pipe_name)
