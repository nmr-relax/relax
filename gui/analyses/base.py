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

# Module docstring.
"""Module containing the base class for all frames."""

# Python module imports.
import wx


class Base_frame:
    """The base class for all frames."""

    def add_title(self, box, text):
        """Create and add the frame title.

        @param box:     The box element to pack the frame title into.
        @type box:      wx.BoxSizer instance
        @param text:    The text of the title.
        @type text:     str
        """

        # The title.
        label = wx.StaticText(self.parent, -1, text)

        # The font properties.
        label.SetFont(self.gui.font_title)

        # Pack the title, with spacing.
        box.AddSpacer(10)
        box.Add(label)
        box.AddSpacer(5)


    def add_subtitle(self, box, text):
        """Create and add the subtitle.

        @param box:     The box element to pack the subtitle into.
        @type box:      wx.BoxSizer instance
        @param text:    The text of the subtitle.
        @type text:     str
        """

        # The title.
        label = wx.StaticText(self.parent, -1, text)

        # The font properties.
        label.SetFont(self.gui.font_subtitle)

        # Add the subtitle to the box, with spacing.
        box.AddSpacer(20)
        box.Add(label)
        box.AddSpacer(5)
