###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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

# Python module imports.
from os import F_OK, access, path, sep
import sys
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()

# relax GUI module imports.
from gui.filedialog import openfile
from gui.icons import relax_icons
from gui.message import error_message
from gui.misc import gui_to_int, int_to_gui
from gui import paths
from gui.wizard import Wiz_page


def load_sequence():
    """GUI element for loading the sequence file."""

    # The dialog.
    seqfile = openfile('Choose a sequence file', '', '', 'all files (*.*)|*.*')

    # No file.
    if not seqfile:
        return None

    # Does not exist.
    if not access(seqfile, F_OK):
        error_message("The file '%s' does not exist." % seqfile)
        return None

    # Not a file.
    if path.isdir(seqfile):
        error_message("The selection '%s' is a directory, not a file." % seqfile)
        return None

    # Return the file.
    return seqfile



class Base_window(wx.Dialog):
    """Base class for the settings windows."""

    # The window size.
    SIZE = (600, 600)

    # A border.
    BORDER = 10

    # Sizes.
    SIZE_BUTTON = (100, 33)

    def __init__(self, parent=None, id=-1, title='', heading='', style=wx.DEFAULT_FRAME_STYLE):
        """Set up the window."""

        # Execute the base __init__() method.
        wx.Dialog.__init__(self, parent, id=id, title=title, style=style)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # The main sizer.
        self.main_sizer = self.build_frame()

        # The heading.
        text = wx.StaticText(self, -1, heading)
        text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.main_sizer.Add(text, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer()

        # The relax logo.
        bmp = wx.StaticBitmap(self, -1, wx.Bitmap(paths.IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.main_sizer.Add(bmp, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer()

        # The centre section.
        self.add_centre(self.main_sizer)

        # The bottom buttons.
        self.add_buttons(self.main_sizer)

        # Set the window size.
        self.SetSize(self.SIZE)
        self.SetMinSize(self.SIZE)

        # Centre the window.
        self.Center()


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 0)

        # The save button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Save")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.save, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Save the free file format settings within the relax data store.")
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.save, button)

        # Spacer.
        button_sizer.AddSpacer(20)

        # The reset button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Reset")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.edit_delete, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Reset the free file format settings to the original values.")
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.reset, button)

        # Spacer.
        button_sizer.AddSpacer(20)

        # The cancel button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Cancel")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.dialog_cancel, wx.BITMAP_TYPE_ANY))
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.cancel, button)


    def add_centre(self, sizer):
        """Dummy base class method for adding the centre of the settings window.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """


    def build_frame(self):
        """Create the main part of the frame, returning the central sizer."""

        # The sizers.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        central_sizer = wx.BoxSizer(wx.VERTICAL)

        # Left and right borders.
        sizer1.AddSpacer(self.BORDER)
        sizer1.Add(sizer2, 1, wx.EXPAND|wx.ALL, 0)
        sizer1.AddSpacer(self.BORDER)

        # Top and bottom borders.
        sizer2.AddSpacer(self.BORDER)
        sizer2.Add(central_sizer, 1, wx.EXPAND|wx.ALL, 0)
        sizer2.AddSpacer(self.BORDER)

        # Set the sizer for the frame.
        self.SetSizer(sizer1)

        # Return the central sizer.
        return central_sizer


    def save(self, event):
        """Dummy base class save method.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Destroy the window.
        self.Destroy()


    def cancel(self, event):
        """Close the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Destroy the window.
        self.Destroy()



class Free_file_format(Base_window, Wiz_page):
    """The free file format setting window."""

    # The window size.
    SIZE = (500, 550)

    def __init__(self, parent=None):
        """Set up the window."""

        # The sizes.
        self._main_size = self.SIZE[0] - 2*self.BORDER
        self._div_left = self._main_size / 2

        # Execute the base __init__() method.
        super(Free_file_format, self).__init__(parent=parent, id=-1, title="Free file format", heading="Settings for the free file format")


    def add_centre(self, sizer):
        """Add the centre of the free file format settings window.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The widget.
        self.free_file_format(sizer, data_cols=True, save=False, reset=False)

        # Spacing.
        self.main_sizer.AddStretchSpacer()


    def reset(self, event):
        """Reset the free file format settings.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the base class method.
        self._free_file_format_reset(event)


    def save(self, event):
        """Save the free file format widget contents into the relax data store.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the base class method.
        self._free_file_format_save(event)

        # Destroy the window.
        self.Destroy()
