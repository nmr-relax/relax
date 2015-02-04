###############################################################################
#                                                                             #
# Copyright (C) 2015 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

"""Memory test of the time GUI user function."""

# Python module imports.
import wx

# Base module imports.
from GUI_base import Testing_frame


class Frame(Testing_frame):
    """Testing frame."""

    def test(self):
        """Run the test."""

        # Repetitive calling of the time user function.
        for i in self.muppy_loop():
            self._execute_uf(uf_name='time')



# Set up and execute the GUI.
app = wx.App(False)
frame = Frame(None, "GUI memory test")
frame.Show(True)
app.MainLoop()
