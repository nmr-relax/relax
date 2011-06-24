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
        main = Main(parent=None, id=-1, title="")

        # Make it the main application component.
        self.app.SetTopWindow(main)

        # Show it.
        main.Show()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data storage object.
        ds.__reset__()

        # Kill the app.
        wx.CallAfter(self.app.Exit)
        self.app.MainLoop()


    def test_noe_analysis(self):
        """Test the NOE analysis."""
