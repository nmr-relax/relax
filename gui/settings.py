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
from gui.message import error_message
from gui.misc import gui_to_int, int_to_gui
from gui import paths
from gui.user_functions.base import UF_window


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



class Base_window(wx.Frame):
    """Base class for the settings windows."""

    # The window size.
    SIZE = (600, 600)

    # A border.
    BORDER = 10

    def __init__(self, parent=None, id=-1, title='', heading='', style=wx.DEFAULT_FRAME_STYLE):
        """Set up the window."""

        # Execute the base __init__() method.
        super(Base_window, self).__init__(parent=parent, id=id, title=title, style=style)

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
        button.SetToolTipString("Save the settings")
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.save, button)

        # Spacer.
        button_sizer.AddSpacer(20)

        # The cancel button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Cancel")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.cancel, wx.BITMAP_TYPE_ANY))
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



class Free_file_format(Base_window, UF_window):
    """The free file format setting window."""

    # The window size.
    SIZE = (500, 550)

    def __init__(self, parent=None):
        """Set up the window."""

        # The sizes.
        self.main_size = self.SIZE[0] - 2*self.BORDER
        self.div_left = self.main_size / 2

        # Execute the base __init__() method.
        super(Free_file_format, self).__init__(parent=parent, id=-1, title="Free file format", heading="Settings for the free file format")


    def add_centre(self, sizer):
        """Add the centre of the free file format settings window.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The widget.
        self.free_file_format(sizer, data_cols=True, save=False)

        # Spacing.
        self.main_sizer.AddStretchSpacer()


    def save(self, event):
        """Save the free file format widget contents into the relax data store.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the base class method.
        self.free_file_format_save(event)

        # Destroy the window.
        self.Destroy()



class Global_params(Base_window, UF_window):
    """The global parameters setting window."""

    # The window size.
    SIZE = (500, 550)

    def __init__(self, parent=None):
        """Set up the window."""

        # The sizes.
        self.main_size = self.SIZE[0] - 2*self.BORDER
        self.div_left = self.main_size / 2

        # Execute the base __init__() method.
        super(Global_params, self).__init__(parent=parent, id=-1, title="Global settings", heading="Global settings")


    def add_centre(self, sizer):
        """Add the centre of the free file format settings window.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The widget.
        self.settings(sizer, save=False)

        # Spacing.
        self.main_sizer.AddStretchSpacer()


    def settings(self, sizer, save=True):
        """Build the free format file settings widget.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @keyword save:      A flag which if True will cause the save button to be displayed.
        @type save:         bool
        """

        # A static box to hold all the widgets.
        box = wx.StaticBox(self, -1, "Set the parameters for optimisation")

        # Init.
        sub_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sub_sizer.AddSpacer(10)
        divider = self.div_left - 15
        padding = 10
        spacer = 3

        # The columns.
        self.bond = self.input_field(sub_sizer, "Bond length:", divider=divider, padding=padding, spacer=spacer)
        self.csa = self.input_field(sub_sizer, "Chemical shift anisotropy (CSA):", divider=divider, padding=padding, spacer=spacer)
        self.hetero = self.input_field(sub_sizer, "Heteronucleus name:", divider=divider, padding=padding, spacer=spacer)
        self.prot = self.input_field(sub_sizer, "Proton name:", divider=divider, padding=padding, spacer=spacer)
        self.grid = self.input_field(sub_sizer, "Grid search increments:", divider=divider, padding=padding, spacer=spacer)
        self.minim = self.input_field(sub_sizer, "Minimisation algorithm:", divider=divider, padding=padding, spacer=spacer)
        self.monte = self.input_field(sub_sizer, "Monte Carlo simulation number:", divider=divider, padding=padding, spacer=spacer)

        # Set the values.
        self.bond.SetValue(int_to_gui(ds.relax_gui.global_setting[0]))
        self.csa.SetValue(int_to_gui(ds.relax_gui.global_setting[1]))
        self.hetero.SetValue(int_to_gui(ds.relax_gui.global_setting[2]))
        self.prot.SetValue(int_to_gui(ds.relax_gui.global_setting[3]))
        self.grid.SetValue(int_to_gui(ds.relax_gui.global_setting[4]))
        self.minim.SetValue(int_to_gui(ds.relax_gui.global_setting[5]))
        self.monte.SetValue(int_to_gui(ds.relax_gui.global_setting[6]))

        # Add a save button.
        if save:
            # A sizer.
            button_sizer = wx.BoxSizer(wx.HORIZONTAL)

            # Build the button.
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, "  Save")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.save, wx.BITMAP_TYPE_ANY))
            button.SetToolTipString("Save the free file format settings within the relax data store")

            # Add the button.
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

            # Right padding.
            button_sizer.AddSpacer(padding)

            # Bind the click event.
            self.Bind(wx.EVT_BUTTON, self.save, button)

            # Add the button sizer to the widget (with spacing).
            sub_sizer.AddSpacer(10-spacer)
            sub_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT|wx.ALL, 0)

        # Set the size of the widget.
        sub_sizer.AddSpacer(10)
        x, y = box.GetSize()
        box.SetMinSize((self.main_size, y))

        # The border of the widget.
        border = wx.BoxSizer()

        # Place the box sizer inside the border.
        border.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(border, 0, wx.EXPAND)
        sizer.AddStretchSpacer()


    def save(self, event):
        """Save the free file format widget contents into the relax data store.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the values.
        ds.relax_gui.global_setting[0] = str(self.bond.GetValue())
        ds.relax_gui.global_setting[1] = str(self.csa.GetValue())
        ds.relax_gui.global_setting[2] = str(self.hetero.GetValue())
        ds.relax_gui.global_setting[3] = str(self.prot.GetValue())
        ds.relax_gui.global_setting[4] = str(self.grid.GetValue())
        ds.relax_gui.global_setting[5] = str(self.minim.GetValue())
        ds.relax_gui.global_setting[6] = str(self.monte.GetValue())

        # Destroy the window.
        self.Destroy()
