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

# Python module imports
from os import sep
import wx

# relax GUI module imports.
from paths import IMAGE_PATH


def dir_message(msg):
    wx.MessageBox(msg, style = wx.OK | wx.ICON_INFORMATION)


def error_message(msg, caption=None):
    """Message box for general errors.

    @param msg:     The message to display.
    @type msg:      str
    """

    # Show the message box.
    wx.MessageBox(msg, caption=caption, style=wx.OK|wx.ICON_ERROR)


def exec_relax():
    check = False
    startrelax = wx.MessageDialog(None, message = 'Start relax?', style = wx.YES_NO | wx.NO_DEFAULT)
    if startrelax.ShowModal() == wx.ID_YES:
        check = True
    else:
        check = False
    return check


def missing_data(missing=[]):
    """Message box GUI element for when a setup is incomplete or there is missing data.

    @keyword missing:   The list of missing data types.
    @type missing:      list of str
    """

    # The message.
    msg = "The set up is incomplete.\n\n"
    if not len(missing):
        msg = msg + "Please check for missing data.\n"
    else:
        msg = msg + "Please check for the following missing information:\n"
    for data in missing:
        msg = msg + "    %s\n" % data

    # The GUI element.
    wx.MessageBox(msg, caption='Missing data', style=wx.OK|wx.ICON_ERROR)


def question(msg, default=False):
    """A generic question box.

    @keyword default:   If True, the default button will be 'yes', otherwise it will be 'no'.
    @type default:      bool
    @return:            The answer.
    @rtype:             bool
    """

    # If default.
    if default:
        style = wx.YES_DEFAULT
    else:
        style = wx.NO_DEFAULT

    # The dialog window.
    dialog = wx.MessageDialog(None, message = msg, style = wx.YES_NO | style)

    answer = False
    if dialog.ShowModal() == wx.ID_YES:
        answer = True

    # Return the answer.
    return answer


def relax_run_ok(msg1):
    wx.MessageBox(msg1, style = wx.OK)



class Relax_is_running(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin relax_is_running.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_1 = wx.StaticText(self, -1, "relax is running...")
        self.bitmap_1 = wx.StaticBitmap(self, -1, wx.Bitmap(IMAGE_PATH+'relax.gif', wx.BITMAP_TYPE_ANY))
        self.abort_relax = wx.Button(self, -1, "Cancel")

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.cancel_relax_run, self.abort_relax)


    def __do_layout(self):
        # begin relax_is_running.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.label_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_1.Add(self.bitmap_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)
        sizer_1.Add(self.abort_relax, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()


    def __set_properties(self):
        # begin relax_is_running.__set_properties
        self.SetTitle("relaxGUI")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.label_1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))


    def cancel_relax_run(self, event): # wxGlade: relax_is_running.<event_handler>
        self.Close()
        event.Skip()
