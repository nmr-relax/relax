###############################################################################
#                                                                             #
# Copyright (C) 2006-2011 Edward d'Auvergne                                   #
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
from unittest import TestCase
import wx

# Dependency checks.
import dep_check

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
if dep_check.wx_module:
    from gui.relax_gui import Main
from status import Status; status = Status()


class Noe(TestCase):
    """Class for testing various aspects specific to the NOE analysis."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Start the GUI.
        self.app = wx.App()

        # Build the GUI.
        self.gui = Main(parent=None, id=-1, title="")

        # Make it the main application component.
        self.app.SetTopWindow(self.gui)


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data storage object.
        ds.__reset__()

        # Kill the app.
        #wx.CallAfter(self.app.Exit)
        self.app.MainLoop()


    def click_new_analysis(self):
        """Simulate a menu click for a new analysis."""

        # The event.
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_MENU_SELECTED, 1)
        self.gui.ProcessEvent(click_event)


    def click_noe_analysis(self):
        """Simulate the clicking of the NOE button in the new analysis wizard."""

        # Wait for the dialog to appear.
        while 1:
            if hasattr(self.gui, 'new_wizard'):
                break

        # The event.
        click_event = wx.CommandEvent(wx.wxEVT_COMMAND_BUTTON_CLICKED, self.gui.new_wizard.wizard.pages[0].button_ids['noe'])
        self.gui.new_wizard.wizard.ProcessEvent(click_event)


    def test_noe_analysis(self):
        """Test the NOE analysis."""

        # Open the new analysis wizard.
        wx.CallAfter(self.click_new_analysis)

        # Select the NOE analysis.
        wx.CallAfter(self.click_noe_analysis)

        # Show the GUI.
        self.gui.Show()
