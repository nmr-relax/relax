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
from generic_fns.pipes import VALID_TYPES

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


    def create(self, event):
        """The pipe.create user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        self._create_window.Show()


    def destroy(self):
        """Close all windows."""

        self._create_window.Destroy()


class Add_window(UF_window):
    """The pipe.create() user function window."""

    # Some class variables.
    size_x = 600
    size_y = 400
    frame_title = 'Add a data pipe'
    image_path = WIZARD_IMAGE_PATH + 'molecule.png'
    main_text = 'This dialog allows you to add new data pipes to the relax data store.'
    title = 'Addition of new data pipes'

    # Some private class variables.
    _spacing = 20


    def _evt_pipe_type(self, event):
        """Selection of the pipe type.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the choice.
        self.pipe_type = str(event.GetString())


    def add_uf(self, sizer):
        """Add the pipe specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Spacer.
        sizer.AddSpacer(self._spacing)

        # The pipe name input.
        sizer.Add(self.pipe_name_element(), 1, wx.ALIGN_TOP|wx.SHAPED, self.border)

        # Spacer.
        sizer.AddSpacer(self._spacing)

        # The type selection.
        sizer.Add(self.pipe_type_element(), 1, wx.ALIGN_TOP, self.border)

        # Spacer.
        sizer.AddSpacer(self._spacing)


    def execute(self):
        """Execute the user function."""

        # Get the name and type.
        pipe_name = str(self.pipe_name.GetValue())

        # Set the name.
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type=self.pipe_type)


    def pipe_name_element(self):
        """Build the pipe name element.

        @return:    The box sizer.
        @rtype:     wx.Sizer instance
        """

        # Init.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The pipe name.
        text = wx.StaticText(self, -1, "The data pipe name:", style=wx.ALIGN_RIGHT)
        sizer.Add(text, 1, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, self.border)

        # The input field.
        self.pipe_name = wx.TextCtrl(self, -1, '')
        self.pipe_name.SetMinSize((50, self.input_size))
        sizer.Add(self.pipe_name, 1, wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, self.border)

        # Return the sizer.
        return sizer


    def pipe_type_element(self):
        """Build the pipe type element.

        @return:    The box sizer.
        @rtype:     wx.Sizer instance
        """

        # Init.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The pipe type.
        text = wx.StaticText(self, -1, "The type of data pipe:", style=wx.ALIGN_LEFT)
        sizer.Add(text, 1, wx.LEFT, self.border)

        # The input field.
        type_choice = wx.Choice(self, -1, style=wx.ALIGN_LEFT, choices=[''] + VALID_TYPES)
        sizer.Add(type_choice, 1, wx.LEFT, self.border)
        self.Bind(wx.EVT_CHOICE, self._evt_pipe_type, type_choice)

        # Return the sizer.
        return sizer
