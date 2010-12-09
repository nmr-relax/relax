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
"""Base class module for the user function GUI elements."""

# Python module imports.
import wx

# relax GUI module imports.
from gui_bieri.controller import Redirect_text


class UF_base:
    """User function GUI element base class."""

    def __init__(self, gui, interpreter):
        """Set up the user function class."""

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # Specific set up.
        self.setup()


    def setup(self):
        """Dummy method to be overwritten."""



class UF_window(wx.Dialog):
    """User function window GUI element base class."""

    # Some class variables.
    size_x = 600
    size_y = 400
    boarder = 5
    image_path = None
    title = ''

    def __init__(self, gui, interpreter, style=wx.DEFAULT_FRAME_STYLE):
        """Set up the user function class."""

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # Execute the base class method.
        wx.Dialog.__init__(self, None, id=-1, title=self.title, style=style)

        # Set up the frame.
        sizer = self.setup_frame()


    def setup_frame(self, layout=wx.VERTICAL):
        """Set up the relax controller frame.

        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Use a grid sizer for packing the elements.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Pack the sizer into the frame.
        self.SetSizer(sizer)

        # Set the default size of the controller.
        self.SetSize((self.size_x, self.size_y))

        # Centre the frame.
        self.Centre()

        # Add the graphics.
        if self.image_path:
            image = wx.StaticBitmap(self, -1, wx.Bitmap(self.image_path, wx.BITMAP_TYPE_ANY))

            # Add the relax logo.
            sizer.Add(image, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, self.border)

        # Return the sizer.
        return sizer


