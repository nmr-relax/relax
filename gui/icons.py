###############################################################################
#                                                                             #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""All of the icons for relax."""

# Python module imports.
from os import sep
import sys
import wx

# relax module imports.
from status import Status; status = Status()


class Relax_icons(wx.IconBundle):
    """The icon bundle class of the main relax icons."""

    def setup(self):
        """Set up the icons after the main app is created."""

        # This is disabled on Macs.
        if not 'darwin' in sys.platform:
            self.AddIconFromFile(status.install_path + sep + 'graphics' + sep + 'ulysses.ico', wx.BITMAP_TYPE_ANY)


class Relax_task_bar_icon(wx.TaskBarIcon):
    """The icon for the Mac OS X task bar."""

    # Set up some ID numbers for the menu entries.
    TBMENU_RESTORE = wx.NewId()
    TBMENU_CLOSE   = wx.NewId()

    def __init__(self, gui):
        """Set up the task bar icon.

        @param gui:     The GUI object.
        @type gui:      wx.Frame instance
        """

        # Store the args.
        self.gui = gui

        # Initilise the base class.
        wx.TaskBarIcon.__init__(self)

        # Set the task bar icon.
        self.SetIcon(wx.Icon(status.install_path + sep + 'graphics' + sep + 'ulysses_shadowless_trans_128x128.png', wx.BITMAP_TYPE_ANY))

        # Bind mouse events.
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.restore)


    def CreatePopupMenu(self):
        """Create and return the task bar menu.

        @return:    The pop up menu.
        @rtype:     wx.Menu instance
        """

        # Initialise the menu.
        popup = wx.Menu()

        # Add some menu entries.
        popup.Append(self.TBMENU_RESTORE, "Restore relax")
        popup.Append(self.TBMENU_CLOSE,   "Exit relax")

        # Bind the menu events.
        self.Bind(wx.EVT_MENU, self.restore, id=self.TBMENU_RESTORE)
        self.Bind(wx.EVT_MENU, self.exit, id=self.TBMENU_CLOSE)

        # Return the menu.
        return popup


    def exit(self, evt):
        """Exit relax from the task bar.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Exit relax.
        wx.CallAfter(self.gui.exit_gui)


    def restore(self, event):
        """Restore relax from the task bar.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Show relax.
        if not self.gui.IsShown():
            self.gui.Show(True)

        # De-iconise relax.
        if self.gui.IsIconized():
            self.gui.Iconize(False)

        # Raise relax to the top of the window hierarchy.
        self.gui.Raise()


# Set up the main set of icons for relax.
relax_icons = Relax_icons()
