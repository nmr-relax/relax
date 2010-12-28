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
from numpy import uint8, zeros
from os import sep
from textwrap import wrap
import webbrowser
import wx
import wx.html

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
    max_x = None
    max_y = None

    # Spacer size (px).
    border = 0

    # Window styles.
    style = wx.BORDER_NONE | wx.STAY_ON_TOP

    # Destroy on clicking.
    DESTROY_ON_CLICK = True

    def __init__(self, parent=None, id=-1, title='', html_text=None):
        """Build the dialog."""

        # Execute the base class __init__() method.
        super(About_base, self).__init__(parent=parent, id=id, title=title, style=self.style)

        # Create a scrolled window.
        self.window = wx.ScrolledWindow(self, -1)

        # Determine the virtual size of the window.
        self.virtual_size()

        # Initialise the y-offset variable.
        self._offset_val = 0

        # The total size.
        self.total_x = self.dim_x + 2*self.border
        self.total_y = self.dim_y + 2*self.border
        self.SetSize((self.total_x, self.total_y))

        # Initialise URL data structures.
        self.url_text = []
        self.url_pos = []

        # Create the buffered device context.
        self.create_buffered_dc()

        # Add HTML content.
        if html_text:
            self.add_html(html_text)

        # Draw everything.
        self.window.Bind(wx.EVT_PAINT, self.generate)

        # Let the dialog be closable with a left button click.
        self.window.Bind(wx.EVT_MOUSE_EVENTS, self.cursor_style)

        # Let the dialog be closable with a left button click.
        self.window.Bind(wx.EVT_LEFT_DOWN, self.process_click)

        # Center Window
        self.Centre()


    def add_html(self, text):
        """Add the given HTML text to the DC.

        @param text:    The HTML text.
        @type text:     str
        """

        # The HTML renderer.
        self.html = wx.html.HtmlDCRenderer()

        # Set the font.
        self.html.SetFonts("Roman", "Courier")

        # Set the DC.
        self.html.SetDC(self.dc, 1.0)

        # Set the size of the HTML object.
        self.html.SetSize(self.virt_x - 2*self.border, self.virt_y - 2*self.border)

        # Add the text.
        self.html.SetHtmlText(text)

        # Render the HTML.
        self.html.Render(self.border, self.border, known_pagebreaks=[])


    def build_widget(self):
        """Dummy widget building method."""


    def create_buffered_dc(self):
        """Build the buffered dc containing the window contents."""

        # The buffer for buffered drawing.
        self.buffer = wx.EmptyBitmap(self.virt_x, self.virt_y)

        # Create the device context.
        self.dc = wx.BufferedDC(None, self.buffer)

        # Set a background.
        self.set_background()

        # Build the rest of the about widget.
        self.build_widget()

        # Finish.
        self.dc.EndDrawing()


    def cursor_style(self, event):
        """Dummy method for not changing the mouse cursor!"""

        # Terminate the event.
        event.Skip()


    def draw_url(self, url_text=None, point_size=11, family=wx.FONTFAMILY_ROMAN):
        """Draw a URL as a hyperlink.

        @keyword url_text:      The text of the url.
        @type url_text:         str
        @keyword point_size:    The size of the text in points.
        @type point_size:       int
        @keyword family:        The font family.
        @type family:           int
        """

        # Set the font.
        font = wx.Font(pointSize=point_size, family=family, style=wx.FONTSTYLE_ITALIC, weight=wx.NORMAL, underline=True)
        self.dc.SetFont(font)
        self.dc.SetTextForeground('#0017aa')

        # The text extent.
        x, y = self.dc.GetTextExtent(url_text)

        # Draw the text, with a spacer.
        text = self.dc.DrawText(url_text, self.border + (self.dim_x - x)/2, self.offset())

        # Store the position of the text (and shift the offset down).
        self.url_pos.append(zeros((2, 2), int))
        self.url_pos[-1][0] = [self.border + (self.dim_x - x)/2, self.border + (self.dim_x + x)/2]
        self.url_pos[-1][1] = [self.offset(), self.offset(y)]

        # Store the URL.
        self.url_text.append(url_text)

        # Restore the old font colour (black).
        self.dc.SetTextForeground('black')


    def draw_title(self, text, point_size=14, family=wx.FONTFAMILY_ROMAN):
        """Draw the title."""

        # Set the font.
        font = wx.Font(point_size, family, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x, y = self.dc.GetTextExtent(text)

        # Draw the text, with a spacer.
        self.dc.DrawText(text, self.border + (self.dim_x - x)/2, self.offset(15))

        # Add the text extent.
        self.offset(y)


    def draw_wrapped_text(self, text, point_size=10, family=wx.FONTFAMILY_ROMAN, width=69, spacer=10):
        """Generic method for drawing wrapped text in the relax about widget.

        @param text:        The text to wrap and draw.
        @type text:         str
        @keyword spacer:    The pixel width of the spacer to place above the text block.
        @type spacer:       int
        """

        # Set the font.
        font = wx.Font(point_size, family, wx.NORMAL, wx.NORMAL)
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
            # Find and break out the URLs from the text.
            text_elements, url = self.split_refs(line)

            # Draw the text.
            x_pos = self.border
            for i in range(len(text_elements)):
                # URL text.
                if url[i]:
                    self.draw_url(url_text=text_elements[i])

                # Add the text.
                else:
                    self.dc.DrawText(text_elements[i], x_pos, self.offset())

                # The new x position.
                x, y = self.dc.GetTextExtent(text_elements[i])
                x_pos += x

            # Update the offset.
            self.offset(max_y + 1)


    def generate(self, event):
        """Build the device context, add the background, and build the dialog.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Create the device context.
        wx.BufferedPaintDC(self.window, self.buffer, wx.BUFFER_VIRTUAL_AREA)


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
        """Determine what to do with the mouse click.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Determine the mouse position.
        x = event.GetX()
        y = event.GetY()

        # A click on a URL.
        for i in range(len(self.url_pos)):
            if x > self.url_pos[i][0, 0] and x < self.url_pos[i][0, 1] and y > self.url_pos[i][1, 0] and y < self.url_pos[i][1, 1]:
                webbrowser.open_new(self.url_text[i])

        # Close the widget.
        if self.DESTROY_ON_CLICK:
            self.Destroy()


    def set_background(self):
        """Build a background for the dialog."""

        # Set a single colour.
        if self.colour1 and not self.colour2:
            self.SetBackgroundColour(self.colour1)

        # A gradient.
        elif self.colour1 and self.colour2:
            self.dc.GradientFillLinear((0, 0, self.virt_x, self.virt_y), self.colour1, self.colour2, wx.SOUTH)


    def split_refs(self, text):
        """Split up text based on the location of URLs.

        @param text:    The text to parse and split up.
        @type text:     str
        @return:        The list of text elements, and a list of flags which if True indicates a corresponding URL in the text list.
        @rtype:         list of str, list of bool
        """

        # Init.
        elements = []
        url = []

        # Walk over the characters.
        for i in range(len(text)):
            # End.
            if len(text) - i < 7:
                break

            # Search for a url.
            if text[i:i+7] == 'http://':
                # Add the text up to here to the list.
                elements.append(text[0:i])
                url.append(False)

                # Find the end.
                end_char = [')', ' ']
                for j in range(i+7, len(text)):
                    if text[j] in end_char:
                        end_i = j
                        break

                # The url.
                elements.append(text[i:j])
                url.append(True)

                # The rest of the text.
                elements.append(text[j:])
                url.append(False)
                
                # Terminate.
                break

        # No URLs.
        if not len(elements):
            elements.append(text)
            url.append(False)

        # Return the data structures.
        return elements, url


    def virtual_size(self):
        """Determine the virtual size of the window."""

        # Dimensions of the drawing area.
        if self.max_x:
            x = self.max_x
        else:
            x = self.dim_x
        if self.max_y:
            y = self.max_y
        else:
            y = self.dim_y

        # Borders.
        self.virt_x = x + 2*self.border
        self.virt_y = y + 2*self.border

        # Set the window virtual size.
        self.window.SetVirtualSize((self.virt_x, self.virt_y))

        # Add y scrolling, if needed.
        self.window.SetScrollRate(0,20)



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
        self.dc.DrawBitmap(bitmap, self.border, self.border, True)



class About_relax(About_base):
    """The about relax dialog."""

    # The relax background colour.
    colour1 = '#e5feff'
    colour2 = '#88cbff'

    # Dimensions.
    dim_x = 450
    dim_y = 580

    # Spacer size (px).
    border = 10

    def __init__(self, parent=None, id=-1, title=''):
        """Build the dialog."""

        # Initialise the program information container.
        self.info = Info_box()

        # The starting cursor type.
        self.cursor_type = 'normal'

        # Execute the base class __init__() method.
        super(About_relax, self).__init__(parent=parent, id=id, title=title)


    def build_widget(self):
        """Build the about dialog."""

        # A global Y offset for packing the elements together (initialise to the border position).
        self.offset(self.border)

        # Draw all the elements.
        self.draw_title(self.info.title + ' ' + self.info.version)
        self.draw_description()
        self.draw_copyright()
        self.offset(10)
        self.draw_url(url_text=self.info.website)
        self.draw_icon()
        self.draw_desc_long()
        self.draw_licence()


    def cursor_style(self, event):
        """Change the mouse cursor when over the url."""

        # Determine the mouse position.
        x = event.GetX()
        y = event.GetY()

        # Selection cursor.
        over_url = False
        for i in range(len(self.url_pos)):
            if x > self.url_pos[i][0, 0] and x < self.url_pos[i][0, 1] and y > self.url_pos[i][1, 0] and y < self.url_pos[i][1, 1]:
                over_url = True

        # Only change if needed.
        if over_url and self.cursor_type == 'normal':
            # Build the cursor.
            select_cursor = wx.StockCursor(wx.CURSOR_HAND)

            # Set the cursor.
            self.window.SetCursor(select_cursor)

            # Reset the cursor type.
            self.cursor_type = 'select'

            # The flag.

        # Normal cursor.
        if not over_url and self.cursor_type == 'select':
            # Build the cursor.
            select_cursor = wx.StockCursor(wx.CURSOR_ARROW)

            # Set the cursor.
            self.window.SetCursor(select_cursor)

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
        self.dc.DrawText(self.info.copyright[0], self.border + (self.dim_x - x1)/2, self.offset(15))
        self.dc.DrawText(self.info.copyright[1], self.border + (self.dim_x - x2)/2, self.offset(y1+3))

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
        self.dc.DrawText(self.info.desc, self.border + (self.dim_x - x)/2, self.offset(15))

        # Add the text extent.
        self.offset(y)


    def draw_icon(self):
        """Draw the relax icon on the canvas."""

        # Add the relax logo.
        self.dc.DrawBitmap(wx.Bitmap(IMAGE_PATH+'ulysses_shadowless_400x168.png'), self.border + (self.dim_x - 400)/2, self.offset(20), True)

        # Add the bitmap width to the offset.
        self.offset(168)


    def draw_licence(self):
        """Draw the relax licence text."""

        self.draw_wrapped_text(self.info.licence, spacer=10)
