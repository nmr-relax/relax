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
"""A standard set of font definitions for consistency throughout the GUI."""

# Python module imports.
import wx


class Font:
    """A storage container for the fonts."""

    def setup(self):
        """To be called by the main wx app, so that the fonts can be initialised correctly."""

        # The fonts.
        self.smaller =     wx.Font(6,  wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.small =       wx.Font(8,  wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.button =      wx.Font(8,  wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.normal =      wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.normal_bold = wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD,   0, "Sans")
        self.subtitle =    wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD,   0, "Sans")
        self.font_14 =     wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")
        self.title =       wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans")

        # Modern fixed-width fonts.
        self.modern_8 = wx.Font(8, wx.MODERN, wx.NORMAL, wx.NORMAL, 0)
        self.modern_10 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, 0)



# Initialise the class for importing.
font = Font()
