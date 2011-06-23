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
"""The pipes user function GUI elements."""

# Python module imports.
import wx

# relax module imports.
from generic_fns.pipes import VALID_TYPES, cdp_name, pipe_names

# GUI module imports.
from base import UF_base, UF_page
from gui.misc import gui_to_str
from gui.paths import WIZARD_IMAGE_PATH
from gui.wizard import Wiz_window


# The container class.
class Pipes(UF_base):
    """The container class for holding all GUI elements."""

    def create(self, event):
        """The pipe.create user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Add a data pipe')
        page = Add_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()


    def copy(self, event):
        """The pipe.copy user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Copy a data pipe')
        page = Copy_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()


    def delete(self, event):
        """The pipe.delete user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=600, size_y=400, title='Delete a data pipe')
        page = Delete_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page)
        wizard.run()


    def switch(self, event):
        """The pipe.switch user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the wizard.
        wizard = Wiz_window(size_x=650, size_y=450, title='Data pipe switching')
        page = Switch_page(wizard, self.gui, self.interpreter)
        wizard.add_page(page, apply_button=False)
        wizard.run()


class Add_page(UF_page):
    """The pipe.create() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = 'This dialog allows you to add new data pipes to the relax data store.'
    title = 'Addition of new data pipes'


    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe name input.
        self.pipe_name = self.input_field(sizer, "The data pipe name:")

        # The type selection.
        self.pipe_type = self.combo_box(sizer, "The type of data pipe:", VALID_TYPES)


    def on_execute(self):
        """Execute the user function."""

        # Get the name and type.
        pipe_name = str(self.pipe_name.GetValue())
        pipe_type = str(self.pipe_type.GetValue())

        # Set the name.
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=pipe_type)



class Copy_page(UF_page):
    """The pipe.copy() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = 'This dialog allows you to copy data pipes.'
    title = 'Data pipe copy'


    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The source pipe.
        self.pipe_from = self.combo_box(sizer, "The source pipe:", [])

        # The destination pipe.
        self.pipe_to = self.input_field(sizer, "The destination pipe name:")


    def on_apply(self, event):
        """Clear the data is apply was hit.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.pipe_from.Clear()

        # Clear the pipe name.
        self.pipe_from.SetValue('')

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_from.Append(name)


    def on_exit(self):
        """Execute the user function."""

        # Get the pipe names.
        pipe_from = gui_to_str(self.pipe_from.GetValue())
        pipe_to = gui_to_str(self.pipe_to.GetValue())

        # Copy the data pipe.
        self.interpreter.pipe.copy(pipe_from, pipe_to)



class Delete_page(UF_page):
    """The pipe.delete() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = 'This dialog allows you to delete data pipes from the relax data store.'
    title = 'Data pipe deletion'


    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe selection.
        self.pipe_name = self.combo_box(sizer, "The pipe:", [])


    def on_execute(self):
        """Execute the user function."""

        # Get the name.
        pipe_name = str(self.pipe_name.GetValue())

        # Delete the data pipe.
        self.interpreter.pipe.delete(pipe_name)


    def on_display(self):
        """Clear and update the pipe name list."""

        # Clear the previous data.
        self.pipe_name.Clear()

        # Clear the pipe name.
        self.pipe_name.SetValue('')

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(name)



class Switch_page(UF_page):
    """The pipe.switch() user function page."""

    # Some class variables.
    image_path = WIZARD_IMAGE_PATH + 'pipe_switch.png'
    main_text = 'This dialog allows you to switch between the various data pipes within the relax data store.'
    title = 'Switch between data pipes'


    def add_contents(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The current data pipe.
        self.cdp = self.text(sizer, "The current data pipe (cdp):")

        # The pipe selection.
        self.pipe_name = self.combo_box(sizer, "The pipe:", [])


    def on_execute(self):
        """Execute the user function."""

        # Get the name.
        pipe_name = str(self.pipe_name.GetValue())

        # Switch the data pipe.
        self.interpreter.pipe.switch(pipe_name)


    def on_display(self):
        """Clear and update the pipe name list and cdp."""

        # Clear the previous data.
        self.pipe_name.Clear()
        self.cdp.Clear()

        # Clear the pipe name.
        self.pipe_name.SetValue('')
        self.cdp.SetValue(str(cdp_name()))

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(name)
