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



# Set up the main set of icons for relax.
relax_icons = Relax_icons()
