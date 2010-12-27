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
import webbrowser
import wx

# relax module imports.
from info import Info_box

# relax GUI module imports.
from paths import IMAGE_PATH



class About_base(wx.Frame):
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
        kwds["style"] = wx.BORDER_NONE | wx.STAY_ON_TOP

        # Execute the base class __init__() method.
        super(About_base, self).__init__(*args, **kwds)

        # Create a scrolled window.
        self.window = wx.ScrolledWindow(self, -1)

        # Initialise the y-offset variable.
        self._offset_val = 0

        # The total size.
        self.total_x = self.dim_x + 2*self.boarder
        self.total_y = self.dim_y + 2*self.boarder
        self.SetSize((self.total_x, self.total_y))

        # Draw everything.
        self.window.Bind(wx.EVT_PAINT, self.generate)

        # Let the dialog be closable with a left button click.
        self.window.Bind(wx.EVT_MOUSE_EVENTS, self.cursor_style)

        # Let the dialog be closable with a left button click.
        self.window.Bind(wx.EVT_LEFT_DOWN, self.process_click)

        # Center Window
        self.Centre()


    def cursor_style(self, event):
        """Dummy method for not changing the mouse cursor!"""

        # Terminate the event.
        event.Skip()


    def draw_title(self, text, point_size=14, family=wx.FONTFAMILY_ROMAN):
        """Draw the title."""

        # Set the font.
        font = wx.Font(point_size, family, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x, y = self.dc.GetTextExtent(text)

        # Draw the text, with a spacer.
        self.dc.DrawText(text, self.boarder + (self.dim_x - x)/2, self.offset(15))

        # Add the text extent.
        self.offset(y)


    def draw_wrapped_text(self, text, text_size=10, width=69, spacer=10):
        """Generic method for drawing wrapped text in the relax about widget.

        @param text:        The text to wrap and draw.
        @type text:         str
        @keyword spacer:    The pixel width of the spacer to place above the text block.
        @type spacer:       int
        """

        # Set the font.
        font = wx.Font(text_size, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # Wrap the text.
        lines = wrap(text, width)

        # Find the max y extent.
        max_y = 0
        for line in lines:
            x, y = self.dc.GetTextExtent(text)
            if y > max_y:
                max_y = y

        # Add a top spacer.
        self.offset(10)

        # Draw.
        for line in lines:
            # Draw the text.
            self.dc.DrawText(line, self.boarder, self.offset())

            # Update the offset.
            self.offset(max_y + 1)


    def generate(self, event):
        """Build the device context, add the background, and build the dialog.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Create the device context.
        self.dc = wx.PaintDC(self.window)

        # Set a background.
        self.set_background()

        # Build the rest of the about widget.
        self.build_widget()


    def offset(self, val=0):
        """Shift the y-offset by the given value and return the new offset.

        @keyword val:   The value to add to the offset (can be negative).
        @type val:      int
        @return:        The new offset.
        @rtype:         int
        """

        # Shift.
        self._offset_val = self._offset_val + val

        # Return.
        return self._offset_val


    def process_click(self, event):
        """Base method which just closes the widget on a click event.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the widget.
        self.Destroy()


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
    dim_x = 450
    dim_y = 580

    # Spacer size (px).
    boarder = 10

    def __init__(self, *args, **kwds):
        """Build the dialog."""

        # Initialise the program information container.
        self.info = Info_box()

        # The starting cursor type.
        self.cursor_type = 'normal'

        # The link position initialisation.
        self.link_pos_x = [0, 0]
        self.link_pos_y = [0, 0]

        # Execute the base class __init__() method.
        super(About_relax, self).__init__(*args, **kwds)


    def build_widget(self):
        """Build the about dialog."""

        # A global Y offset for packing the elements together (initialise to the boarder position).
        self.offset(self.boarder)

        # Draw all the elements.
        self.draw_title(self.info.title + ' ' + self.info.version)
        self.draw_description()
        self.draw_copyright()
        self.draw_link()
        self.draw_icon()
        self.draw_desc_long()
        self.draw_licence()


    def cursor_style(self, event):
        """Change the mouse cursor when over the link."""

        # Determine the mouse position.
        x = event.GetX()
        y = event.GetY()

        # Selection cursor.
        if x > self.link_pos_x[0] and x < self.link_pos_x[1] and y > self.link_pos_y[0] and y < self.link_pos_y[1]:
            # Only change if needed.
            if self.cursor_type == 'normal':
                # Build the cursor.
                select_cursor = wx.StockCursor(wx.CURSOR_HAND)

                # Set the cursor.
                self.SetCursor(select_cursor)

                # Reset the cursor type.
                self.cursor_type = 'select'

        # Normal cursor.
        elif self.cursor_type == 'select':
            # Build the cursor.
            select_cursor = wx.StockCursor(wx.CURSOR_ARROW)

            # Set the cursor.
            self.SetCursor(select_cursor)

            # Reset the cursor type.
            self.cursor_type = 'normal'


    def draw_copyright(self):
        """Draw the copyright statements."""

        # Set the font.
        font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x1, y1 = self.dc.GetTextExtent(self.info.copyright[0])
        x2, y2 = self.dc.GetTextExtent(self.info.copyright[1])

        # Draw the text, with a starting spacer.
        self.dc.DrawText(self.info.copyright[0], self.boarder + (self.dim_x - x1)/2, self.offset(15))
        self.dc.DrawText(self.info.copyright[1], self.boarder + (self.dim_x - x2)/2, self.offset(y1+3))

        # Add the text extent.
        self.offset(y2)


    def draw_desc_long(self):
        """Draw the long relax description."""

        self.draw_wrapped_text(self.info.desc_long, spacer=10)


    def draw_description(self):
        """Draw the relax description text."""

        # Set the font.
        font = wx.Font(12, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x, y = self.dc.GetTextExtent(self.info.desc)

        # Draw the text, with a spacer.
        self.dc.DrawText(self.info.desc, self.boarder + (self.dim_x - x)/2, self.offset(15))

        # Add the text extent.
        self.offset(y)


    def draw_icon(self):
        """Draw the relax icon on the canvas."""

        # Add the relax logo.
        self.dc.DrawBitmap(wx.Bitmap(IMAGE_PATH+'ulysses_shadowless_400x168.png'), self.boarder + (self.dim_x - 400)/2, self.offset(20), True)

        # Add the bitmap width to the offset.
        self.offset(168)


    def draw_licence(self):
        """Draw the relax licence text."""

        self.draw_wrapped_text(self.info.licence, spacer=10)


    def draw_link(self):
        """Draw the relax description text."""

        # Set the font.
        font = wx.Font(pointSize=11, family=wx.FONTFAMILY_ROMAN, style=wx.FONTSTYLE_ITALIC, weight=wx.NORMAL, underline=True)
        self.dc.SetFont(font)
        self.dc.SetTextForeground('#0017aa')

        # Add a spacer.
        self.offset(10)

        # The text extent.
        x, y = self.dc.GetTextExtent(self.info.website)

        # Draw the text, with a spacer.
        text = self.dc.DrawText(self.info.website, self.boarder + (self.dim_x - x)/2, self.offset())

        # Store the position of the text (and shift the offset down).
        self.link_pos_x = [self.boarder + (self.dim_x - x)/2, self.boarder + (self.dim_x + x)/2]
        self.link_pos_y = [self.offset(), self.offset(y)]

        # Restore the old font colour (black).
        self.dc.SetTextForeground('black')


    def process_click(self, event):
        """Determine what to do with the mouse click.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Determine the mouse position.
        x = event.GetX()
        y = event.GetY()

        # A click on the relax link.
        if x > self.link_pos_x[0] and x < self.link_pos_x[1] and y > self.link_pos_y[0] and y < self.link_pos_y[1]:
            webbrowser.open_new(self.info.website)

        # Close the dialog on all clicks.
        self.Destroy()
