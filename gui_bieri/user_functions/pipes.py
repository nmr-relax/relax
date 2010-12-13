###############################################################################
#                                                                             #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
from generic_fns.pipes import VALID_TYPES, pipe_names

# GUI module imports.
from base import UF_base, UF_window
from gui_bieri.paths import WIZARD_IMAGE_PATH


# The container class.
class Pipes(UF_base):
    """The container class for holding all GUI elements."""

    def setup(self):
        """Place all the GUI classes into this class for storage."""

        # The dialogs.
        self._create_window = Add_window(self.gui, self.interpreter)
        self._delete_window = Delete_window(self.gui, self.interpreter)
        self._switch_window = Switch_window(self.gui, self.interpreter)


    def create(self, event):
        """The pipe.create user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._create_window.Show()


    def delete(self, event):
        """The pipe.delete user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._delete_window.Show()


    def switch(self, event):
        """The pipe.switch user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._switch_window.Show()


    def destroy(self):
        """Close all windows."""

        self._create_window.Destroy()
        self._delete_window.Destroy()
        self._switch_window.Destroy()



class Add_window(UF_window):
    """The pipe.create() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Add a data pipe'
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = 'This dialog allows you to add new data pipes to the relax data store.'
    title = 'Addition of new data pipes'


    def add_uf(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe name input.
        self.pipe_name = self.input_field(sizer, "The data pipe name:")

        # The type selection.
        self.pipe_type = self.combo_box(sizer, "The type of data pipe:", [''] + VALID_TYPES)


    def execute(self):
        """Execute the user function."""

        # Get the name and type.
        pipe_name = str(self.pipe_name.GetValue())
        pipe_type = str(self.pipe_type.GetValue())

        # Set the name.
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=pipe_type)



class Delete_window(UF_window):
    """The pipe.delete() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Delete a data pipe'
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = 'This dialog allows you to delete data pipes from the relax data store.'
    title = 'Data pipe deletion'


    def add_uf(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe selection.
        self.pipe_name = self.combo_box(sizer, "The pipe:", [])


    def execute(self):
        """Execute the user function."""

        # Get the name.
        pipe_name = str(self.pipe_name.GetValue())

        # Delete the data pipe.
        self.interpreter.pipe.delete(pipe_name)

        # Update.
        self.update(None)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.pipe_name.Clear()

        # Clear the pipe name.
        self.pipe_name.SetValue('')

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(name)



class Switch_window(UF_window):
    """The pipe.switch() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    button_apply = False
    frame_title = 'Data pipe switching'
    image_path = WIZARD_IMAGE_PATH + 'pipe.png'
    main_text = 'This dialog allows you to switch between the various data pipes within the relax data store.'
    title = 'Switch between data pipes'


    def add_uf(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The pipe selection.
        self.pipe_name = self.combo_box(sizer, "The pipe:", [])


    def execute(self):
        """Execute the user function."""

        # Get the name.
        pipe_name = str(self.pipe_name.GetValue())

        # Switch the data pipe.
        self.interpreter.pipe.switch(pipe_name)


    def update(self, event):
        """Update the UI.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous data.
        self.pipe_name.Clear()

        # Clear the pipe name.
        self.pipe_name.SetValue('')

        # The list of pipe names.
        for name in pipe_names():
            self.pipe_name.Append(name)
