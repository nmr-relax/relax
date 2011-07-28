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

# Python module imports
from os import sep
import sys
import wx
import wx.lib.buttons
import wx.lib.scrolledpanel

# relax module imports.
from status import Status; status = Status()

# relax GUI module imports.
from gui.icons import relax_icons
from gui.paths import IMAGE_PATH, icon_22x22, icon_48x48
import gui


def dir_message(msg):
    wx.MessageBox(msg, style = wx.OK | wx.ICON_INFORMATION)


def error_message(msg, caption=''):
    """Message box for general errors.

    @param msg:     The message to display.
    @type msg:      str
    """

    # Show the message box.
    if status.show_gui:
        wx.MessageBox(msg, caption=caption, style=wx.OK|wx.ICON_ERROR)


    # Otherwise throw the error out to stderr.
    else:
        # Combine the caption and message.
        if caption:
            msg = "%s:  %s" % (caption, msg)

        # Write out.
        sys.stderr.write(msg + "\n")


def exec_relax():
    check = False
    startrelax = wx.MessageDialog(None, message = 'Start relax?', style = wx.YES_NO | wx.NO_DEFAULT)
    if startrelax.ShowModal() == wx.ID_YES:
        check = True
    else:
        check = False
    return check


def relax_run_ok(msg1):
    """Message box stating that the relax run completed ok."""

    # Show the message box.
    if status.show_gui:
        wx.MessageBox(msg1, style = wx.OK)



class Missing_data(wx.Dialog):
    """Message box GUI element for when a setup is incomplete or there is missing data."""

    def __init__(self, missing=[]):
        """Set up the dialog.

        @keyword missing:   The list of missing data types.
        @type missing:      list of str
        """

        # Initialise the base class.
        wx.Dialog.__init__(self, None, title='Missing data', style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Set the initial size.
        self.SetSize((600, 400))

        # A sizer for the dialog.
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = gui.misc.add_border(main_sizer, border=10, packing=wx.HORIZONTAL)

        # Add the graphic.
        bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(icon_48x48.user_busy, wx.BITMAP_TYPE_ANY))
        sizer.Add(bitmap)

        # Spacing.
        sizer.AddSpacer(20)

        # A scrolled panel for the text.
        panel = wx.lib.scrolledpanel.ScrolledPanel(self, -1)
        panel.SetAutoLayout(1)
        panel.SetupScrolling()
        sizer.Add(panel, 1, wx.ALL|wx.EXPAND, 0)

        # A sizer for the panel.
        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(panel_sizer)

        # The message.
        msg = "The set up is incomplete.\n\n"
        if not len(missing):
            msg = msg + "Please check for missing data.\n"
        else:
            msg = msg + "Please check for the following missing information:\n"
        for data in missing:
            msg = msg + "    %s\n" % data

        # Convert to a text element.
        text = wx.StaticText(panel, -1, msg, style=wx.TE_MULTILINE)
        panel_sizer.Add(text)

        # Show the GUI element.
        if status.show_gui:
            self.ShowModal()

        # Otherwise throw the error out to stderr.
        else:
            sys.stderr.write("Missing data:  %s\n" % msg)



class Question(wx.Dialog):
    """Question box GUI element for obtaining a yes/no response from the user."""

    # Some class variables.
    border = 10
    spacer_button = 10
    spacer_main = 20
    height_button = 30
    width_button = 50

    def __init__(self, msg, title='', size=(350, 125), default=False):
        """A generic question box.

        @param msg:         The text message to display.
        @type msg:          str
        @keyword title:     The window title.
        @type title:        str
        @keyword default:   If True, the default button will be 'yes', otherwise it will be 'no'.
        @type default:      bool
        @return:            The answer.
        @rtype:             bool
        """

        # The default.
        if default:
            self.answer = wx.ID_YES
        else:
            self.answer = wx.ID_NO

        # Initialise the base class.
        wx.Dialog.__init__(self, None, title=title, size=size, style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # A sizer for the dialog.
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = gui.misc.add_border(main_sizer, border=self.border, packing=wx.HORIZONTAL)

        # Add the graphic.
        bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(icon_48x48.dialog_warning, wx.BITMAP_TYPE_ANY))
        sizer.Add(bitmap)

        # Spacing.
        sizer.AddSpacer(self.spacer_main)

        # A vertical sizer for the right hand contents.
        sub_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Convert to a text element.
        text = wx.StaticText(self, -1, msg, style=wx.TE_MULTILINE)
        sub_sizer.Add(text, 1, wx.ALL|wx.EXPAND, 0)

        # A sizer for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sub_sizer.Add(button_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # The yes button.
        button_yes = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Yes")
        button_yes.SetBitmapLabel(wx.Bitmap(icon_22x22.dialog_ok, wx.BITMAP_TYPE_ANY))
        button_yes.SetMinSize((self.width_button, self.height_button))
        button_sizer.Add(button_yes, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        self.Bind(wx.EVT_BUTTON, self.yes, button_yes)

        # Button spacing.
        button_sizer.AddSpacer(self.spacer_button)

        # The no button.
        button_no = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " No")
        button_no.SetBitmapLabel(wx.Bitmap(icon_22x22.dialog_cancel, wx.BITMAP_TYPE_ANY))
        button_no.SetMinSize((self.width_button, self.height_button))
        button_sizer.Add(button_no, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        self.Bind(wx.EVT_BUTTON, self.no, button_no)

        # Set the focus to the default button.
        if self.answer == wx.ID_YES:
            button_yes.SetFocus()
        else:
            button_no.SetFocus()


    def ShowModal(self):
        """Replacement ShowModal method.
        
        @return:    The answer to the question, either wx.ID_YES or wx.ID_NO.
        @rtype:     int
        """

        # Call the dialog's ShowModal method.
        if status.show_gui:
            super(Question, self).ShowModal()

        # Return the answer.
        return self.answer


    def no(self, event):
        """No selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the answer.
        self.answer = wx.ID_NO

        # Close the dialog.
        self.Close()


    def yes(self, event):
        """Yes selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the answer.
        self.answer = wx.ID_YES

        # Close the dialog.
        self.Close()
