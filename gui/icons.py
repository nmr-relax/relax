###############################################################################
#                                                                             #
# Copyright (C) 2011,2019 Edward d'Auvergne                                   #
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

# Module docstring.
"""All of the icons for relax."""

# Python module imports.
from os import sep
import sys
import wx

# relax module imports.
import dep_check
from status import Status; status = Status()


class Relax_icons(wx.IconBundle):
    """The icon bundle singleton class of the main relax icons."""

    # Class variable for storing the class instance (for the singleton).
    _instance = None

    def __new__(self, *args, **kargs):
        """Replacement method for implementing the singleton design pattern."""

        # First instantiation.
        if self._instance is None:
            # Instantiate.
            self._instance = wx.IconBundle.__new__(self, *args, **kargs)

        # Already instantiated, so return the instance.
        return self._instance


    def setup(self):
        """Set up the icons after the main app is created."""

        # This is disabled on Macs.
        if not 'darwin' in sys.platform:
            if dep_check.wx_classic:
                self.AddIconFromFile(status.install_path + sep + 'graphics' + sep + 'ulysses.ico', wx.BITMAP_TYPE_ANY)
            else:
                self.AddIcon(status.install_path + sep + 'graphics' + sep + 'ulysses.ico', wx.BITMAP_TYPE_ANY)
