###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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

# Python module imports.
from os import F_OK, access, path, sep
import sys
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()

# relax GUI module imports.
from gui_bieri.filedialog import openfile
from gui_bieri.message import error_message
from gui_bieri.misc import gui_to_int, int_to_gui
from gui_bieri import paths
from gui_bieri.user_functions.base import UF_window


def relax_global_settings(oldsettings):
    global settings
    global old_settings
    settings = []
    old_settings = oldsettings
    set_relax_params = Globalparam(None, -1, "")
    set_relax_params.ShowModal()
    return settings


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

        # Get the column numbers.
        ds.relax_gui.free_file_format.spin_id_col =   gui_to_int(self.spin_id_col.GetValue())
        ds.relax_gui.free_file_format.mol_name_col =  gui_to_int(self.mol_name_col.GetValue())
        ds.relax_gui.free_file_format.res_num_col =   gui_to_int(self.res_num_col.GetValue())
        ds.relax_gui.free_file_format.res_name_col =  gui_to_int(self.res_name_col.GetValue())
        ds.relax_gui.free_file_format.spin_num_col =  gui_to_int(self.spin_num_col.GetValue())
        ds.relax_gui.free_file_format.spin_name_col = gui_to_int(self.spin_name_col.GetValue())

        # The column separator.
        ds.relax_gui.free_file_format.sep = str(self.sep.GetValue())
        if ds.relax_gui.free_file_format.sep == 'white space':
            ds.relax_gui.free_file_format.sep = None

        # Destroy the window.
        self.Destroy()



class Globalparam(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin globalparam.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1_copy = wx.StaticText(self, -1, "Set the parameters for optimisation")
        self.bitmap_1_copy = wx.StaticBitmap(self, -1, wx.Bitmap(paths.IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.label_2_copy = wx.StaticText(self, -1, "Bond length")
        self.bond = wx.TextCtrl(self, -1, old_settings[0])
        self.label_3_copy = wx.StaticText(self, -1, "Chemical shift anisotropy (CSA)")
        self.csa = wx.TextCtrl(self, -1, old_settings[1])
        self.label_5_copy = wx.StaticText(self, -1, "Heteronucleus name")
        self.hetero = wx.TextCtrl(self, -1, old_settings[2])
        self.label_6_copy = wx.StaticText(self, -1, "Proton name")
        self.prot = wx.TextCtrl(self, -1, old_settings[3])
        self.label_9_copy = wx.StaticText(self, -1, "Grid search increments")
        self.grid = wx.TextCtrl(self, -1, old_settings[4])
        self.label_7_copy = wx.StaticText(self, -1, "Minimisation algorithm")
        self.minim = wx.TextCtrl(self, -1, old_settings[5])
        self.label_8_copy = wx.StaticText(self, -1, "Monte Carlo simulation number")
        self.monte = wx.TextCtrl(self, -1, old_settings[6])
        self.ok_copy = wx.Button(self, -1, "Ok")
        self.cancel_copy = wx.Button(self, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.accept_settings, self.ok_copy)
        self.Bind(wx.EVT_BUTTON, self.cancel_settings, self.cancel_copy)
        self.Bind(wx.EVT_CLOSE, self.cancel_settings)


    def __do_layout(self):
        # begin  globalparam.__do_layout
        sizer_1_copy = wx.BoxSizer(wx.VERTICAL)
        grid_sizer_1_copy = wx.FlexGridSizer(8, 2, 0, 0)
        sizer_1_copy.Add(self.label_1_copy, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer_1_copy.Add(self.bitmap_1_copy, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        grid_sizer_1_copy.Add(self.label_2_copy, 1, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.bond, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_3_copy, 1, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.csa, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_5_copy, 1, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.hetero, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_6_copy, 1, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.prot, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_9_copy, 1, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.grid, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_7_copy, 1, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.minim, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.Add(self.label_8_copy, 1, wx.LEFT, 5)
        grid_sizer_1_copy.Add(self.monte, 1, wx.EXPAND, 0)
        grid_sizer_1_copy.AddGrowableCol(1)
        sizer_1_copy.Add(grid_sizer_1_copy, 1, wx.EXPAND|wx.ALL, 5)
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2.Add(self.ok_copy, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        sizer2.Add(self.cancel_copy, 0, wx.ALL, 5)
        sizer_1_copy.Add(sizer2, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_1_copy)
        sizer_1_copy.Fit(self)
        self.Layout()


    def __set_properties(self):
        # begin globalparam.__set_properties
        self.SetTitle("Global parameters")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(paths.IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_1_copy.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.bond.SetMinSize((250, 27))
        self.csa.SetMinSize((250, 27))
        self.hetero.SetMinSize((250, 27))
        self.prot.SetMinSize((250, 27))
        self.grid.SetMinSize((250, 27))
        self.minim.SetMinSize((250, 27))
        self.label_8_copy.SetMinSize((250, 17))
        self.monte.SetMinSize((250, 27))


    def accept_settings(self, event): # change settings
        global settings
        settings = []
        settings.append(str(self.bond.GetValue()))
        settings.append(str(self.csa.GetValue()))
        settings.append(str(self.hetero.GetValue()))
        settings.append(str(self.prot.GetValue()))
        settings.append(str(self.grid.GetValue()))
        settings.append(str(self.minim.GetValue()))
        settings.append(str(self.monte.GetValue()))
        self.Destroy()
        event.Skip()


    def cancel_settings(self, event): # do not change settings
        global settings
        settings = None
        self.Destroy()
        event.Skip()
