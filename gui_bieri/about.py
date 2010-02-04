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

# Python module imports.
from os import sep
from textwrap import wrap
import wx

# relax module imports.
from intro import Intro_text

# relax GUI module imports.
from paths import IMAGE_PATH



class About_base(wx.Dialog):
    """The about dialog base class."""

    # The background colour (gradient if second colour is given).
    colour1 = None
    colour2 = None

    # Dimensions.
    dim_x = 400
    dim_y = 600

    # Spacer size (px).
    boarder = 0

    def __init__(self, *args, **kwds):
        """Build the dialog."""

        # Change the dialog style.
        kwds["style"] = wx.BORDER_NONE

        # Execute the base class __init__() method.
        super(About_base, self).__init__(*args, **kwds)

        # The total size.
        self.total_x = self.dim_x + 2*self.boarder
        self.total_y = self.dim_y + 2*self.boarder
        self.SetMinSize((self.total_x, self.total_y))

        # Draw everything.
        self.Bind(wx.EVT_PAINT, self.generate)

        # Let the dialog be closable with a left button click.
        self.Bind(wx.EVT_LEFT_DOWN, self.close)


    def close(self, event):
        """Close the dialog.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close.
        self.Close()

        # Terminate the event.
        event.Skip()


    def generate(self, event):
        """Build the device context, add the background, and build the dialog.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Create the device context.
        self.dc = wx.PaintDC(self)

        # Set a background.
        self.set_background()

        # Build the rest of the about widget.
        self.build_widget()


    def set_background(self):
        """Build a background for the dialog."""

        # Set a single colour.
        if self.colour1 and not self.colour2:
            self.SetBackgroundColour(self.colour1)

        # A gradient.
        elif self.colour1 and self.colour2:
            self.dc.GradientFillLinear((0, 0, self.total_x, self.total_y), self.colour1, self.colour2, wx.SOUTH)



class About_gui(About_base):
    """The about relax GUI dialog."""

    # The background colour.
    colour1 = 'white'

    # Dimensions.
    dim_x = 640
    dim_y = 480

    def build_widget(self):
        """Build the about dialog."""

        # The image.
        bitmap = wx.Bitmap(IMAGE_PATH+'start.png', wx.BITMAP_TYPE_ANY)

        # Draw it.
        self.dc.DrawBitmap(bitmap, self.boarder, self.boarder, True)



class About_relax(About_base):
    """The about relax dialog."""

    # The relax background colour.
    colour1 = '#e5feff'
    colour2 = '#88cbff'

    # Dimensions.
    dim_x = 400
    dim_y = 600

    # Spacer size (px).
    boarder = 10

    def __init__(self, *args, **kwds):
        """Build the dialog."""

        # Initialise the program information container.
        self.info = Intro_text()

        # Execute the base class __init__() method.
        super(About_relax, self).__init__(*args, **kwds)


    def build_widget(self):
        """Build the about dialog."""

        # The relax icon.
        self.draw_icon()

        # The title.
        self.draw_title()

        # The description.
        self.draw_description()

        # The copyright.
        self.draw_copyright()

        # The licence.
        self.draw_licence()


    def draw_copyright(self):
        """Draw the copyright statements."""

        # Set the font.
        font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # Offset.
        offset = 270

        # The text extent.
        x1, y1 = self.dc.GetTextExtent(self.info.copyright[0])
        x2, y2 = self.dc.GetTextExtent(self.info.copyright[1])

        # Draw the text.
        self.dc.DrawText(self.info.copyright[0], self.boarder + (self.dim_x - x1)/2, offset)
        self.dc.DrawText(self.info.copyright[1], self.boarder + (self.dim_x - x2)/2, offset+y1+3)


    def draw_description(self):
        """Draw the relax description text."""

        # Set the font.
        font = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x, y = self.dc.GetTextExtent(self.info.desc)

        # Draw the text.
        self.dc.DrawText(self.info.desc, self.boarder + (self.dim_x - x)/2, 230)


    def draw_icon(self):
        """Draw the relax icon on the canvas."""

        # Add the relax logo.
        self.dc.DrawBitmap(wx.Bitmap(IMAGE_PATH+'ulysses_shadowless_400x168.png'), self.boarder, self.boarder, True)


    def draw_licence(self):
        """Draw the relax licence text."""

        # Set the font.
        font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # Offset.
        offset = 325

        # Wrap the text.
        lines = wrap(self.info.licence, 60)

        # Find the max y extent.
        max_y = 0
        for line in lines:
            x, y = self.dc.GetTextExtent(self.info.desc)
            if y > max_y:
                max_y = y

        # Draw.
        for line in lines:
            # Draw the text.
            self.dc.DrawText(line, self.boarder, offset)

            # Update the offset.
            offset = offset + max_y + 1


    def draw_title(self):
        """Draw the relax title with name and version."""

        # The text.
        text = self.info.title + ' ' + self.info.version

        # Set the font.
        font = wx.Font(14, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x, y = self.dc.GetTextExtent(text)

        # Draw the text.
        self.dc.DrawText(text, self.boarder + (self.dim_x - x)/2, 20+168)
