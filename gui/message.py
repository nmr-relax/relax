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

# relax module imports.
from status import Status; status = Status()

# relax GUI module imports.
from paths import IMAGE_PATH


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
    if status.show_gui:
        wx.MessageBox(msg, caption='Missing data', style=wx.OK|wx.ICON_ERROR)

    # Otherwise throw the error out to stderr.
    else:
        sys.stderr.write("Missing data:  %s\n" % msg)


def question(msg, caption='', default=False):
    """A generic question box.

    @param msg:         The text message to display.
    @type msg:          str
    @keyword caption:   The window title.
    @type caption:      str
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
    dialog = wx.MessageDialog(None, message=msg, caption=caption, style=wx.YES_NO|style)

    # The answer.
    answer = False

    # No GUI, so always answer True.
    if not status.show_gui:
        answer = True

    # Otherwise get the answer from the user.
    elif dialog.ShowModal() == wx.ID_YES:
        answer = True

    # Return the answer.
    return answer


def relax_run_ok(msg1):
    """Message box stating that the relax run completed ok."""

    # Show the message box.
    if status.show_gui:
        wx.MessageBox(msg1, style = wx.OK)
