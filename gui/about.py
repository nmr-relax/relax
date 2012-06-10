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

# Python module imports.
from copy import deepcopy
from numpy import uint8, zeros
from os import sep
from string import split
import webbrowser
import wx
import wx.html
from wx.lib.wordwrap import wordwrap

# relax module imports.
from info import Info_box
from status import Status; status = Status()

# relax GUI module imports.
from gui.icons import relax_icons
from gui.paths import IMAGE_PATH


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

    # Scrolling rate.
    SCROLL_RATE = 20

    def __init__(self, parent=None, id=-1, title='', html_text=None):
        """Build the dialog."""

        # Execute the base class __init__() method.
        super(About_base, self).__init__(parent=parent, id=id, title=title, style=self.style)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Create a scrolled window.
        self.window = wx.ScrolledWindow(self, -1)

        # Initialise the y-offset variable.
        self._offset_val = 0

        # The starting cursor type.
        self.cursor_type = 'normal'

        # Initialise URL data structures.
        self.url_text = []
        self.url_pos = []

        # Determine the virtual size of the window.
        self.text_max_x = 0
        self.virtual_size()

        # Set the window size.
        self.SetSize((self.virt_x, self.dim_y))

        # Set the window virtual size.
        self.window.SetVirtualSize((self.virt_x, self.virt_y))

        # Add y scrolling, if needed.
        self.window.SetScrollRate(0, self.SCROLL_RATE)

        # Create the buffered device context.
        self.create_buffered_dc()

        # Add HTML content.
        if html_text:
            self.add_html(html_text)

        # Draw everything.
        self.window.Bind(wx.EVT_PAINT, self.generate)

        # Let the dialog be closable with a left button click.
        self.window.Bind(wx.EVT_MOTION, self.cursor_style)

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
        self.html.SetSize(self.virt_x, self.virt_y)

        # Add the text.
        self.html.SetHtmlText(text)

        # Render the HTML.
        self.html.Render(self.border, self.border, known_pagebreaks=[])


    def build_widget(self):
        """Dummy widget building method."""


    def create_buffered_dc(self):
        """Build the buffered dc containing the window contents."""

        # The buffer for buffered drawing (work around for a GTK bug, the bitmap must be square!!!).
        size = max(self.virt_x, self.virt_y)
        self.buffer = wx.EmptyBitmap(size, size)

        # Create the device context.
        self.dc = wx.BufferedDC(None, self.buffer)

        # Set a background.
        self.set_background()

        # Debugging lines.
        if status.debug:
            # Cross.
            self.dc.DrawLine(0, 0, self.virt_x, self.virt_y)
            self.dc.DrawLine(self.virt_x, 0, 0, self.virt_y)

            # Lines every 200 pixels.
            num = self.virt_y / 200
            for i in range(num):
                pos = i * 200
                self.dc.DrawLine(0, pos, self.virt_x, pos) 
                self.dc.SetFont(wx.Font(8, wx.FONTFAMILY_SCRIPT, wx.NORMAL, wx.NORMAL))
                self.dc.DrawText(str(pos), self.virt_x-40, pos-10)


        # Build the rest of the about widget.
        self.build_widget()

        # Finish.
        self.dc.EndDrawing()


    def cursor_style(self, event):
        """Change the mouse cursor when over the url."""

        # Determine the mouse position.
        x = event.GetX()
        y = event.GetY()

        # Scrolling.
        y = y + self.window.GetViewStart()[1]*self.SCROLL_RATE

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

        # Normal cursor.
        if not over_url and self.cursor_type == 'select':
            # Build the cursor.
            select_cursor = wx.StockCursor(wx.CURSOR_ARROW)

            # Set the cursor.
            self.window.SetCursor(select_cursor)

            # Reset the cursor type.
            self.cursor_type = 'normal'


    def draw_url(self, url_text=None, point_size=11, family=wx.FONTFAMILY_ROMAN, pos_x=0, carriage_ret=False, centre=False):
        """Draw a URL as a hyperlink.

        @keyword url_text:      The text of the url.
        @type url_text:         str
        @keyword point_size:    The size of the text in points.
        @type point_size:       int
        @keyword family:        The font family.
        @type family:           int
        @keyword pos_x:         The starting x position for the text.
        @type pos_x:            int
        @keyword carriage_ret:  A flag which if True will cause a carriage return, by shifting the offset by y.
        @type carriage_ret:     bool
        @keyword centre:        A flag which if True will cause the URL to be centred in the window.
        @type centre:           bool
        """

        # Get the original font.
        orig_font = self.dc.GetFont()
        orig_fg = deepcopy(self.dc.GetTextForeground())

        # Set the font.
        font = wx.Font(pointSize=point_size, family=family, style=wx.NORMAL, weight=wx.NORMAL)
        self.dc.SetFont(font)
        self.dc.SetTextForeground('#0017aa')

        # The text extent.
        x, y = self.dc.GetTextExtent(url_text)

        # Draw the text centred.
        if centre:
            pos_x = (self.dim_x - x)/2

        # Draw the text.
        text = self.dc.DrawText(url_text, pos_x, self.offset())

        # Store the position of the text.
        self.url_pos.append(zeros((2, 2), int))
        self.url_pos[-1][0] = [pos_x, pos_x + x]
        self.url_pos[-1][1] = [self.offset(), self.offset()+y]

        # Shift down.
        if carriage_ret:
            self.offset(y)

        # Store the URL.
        self.url_text.append(url_text)

        # Restore the original font.
        self.dc.SetFont(orig_font)
        self.dc.SetTextForeground(orig_fg)


    def draw_title(self, text, point_size=14, family=wx.FONTFAMILY_ROMAN):
        """Draw the title."""

        # Set the font.
        font = wx.Font(point_size, family, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x, y = self.dc.GetTextExtent(text)

        # Draw the text, with a spacer.
        self.dc.DrawText(text, (self.virt_x - x)/2, self.offset(15))

        # Add the text extent.
        self.offset(y)


    def draw_wrapped_text(self, text, point_size=10, family=wx.FONTFAMILY_ROMAN, spacer=10):
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
        width = self.dim_x - 2*self.border
        wrapped_text = wordwrap(text, width, self.dc)

        # Find the full extents.
        full_x, full_y = self.dc.GetTextExtent(wrapped_text)

        # Add a top spacer.
        self.offset(10)

        # Draw.
        lines = split(wrapped_text, '\n')
        for line in lines:
            # Find and break out the URLs from the text.
            text_elements, url = self.split_refs(line)

            # Draw the text.
            pos_x = self.border
            for i in range(len(text_elements)):
                # URL text.
                if url[i]:
                    self.draw_url(point_size=point_size, family=family, url_text=text_elements[i], pos_x=pos_x)

                # Add the text.
                else:
                    self.dc.DrawText(text_elements[i], pos_x, self.offset())

                # The new x position.
                x, y = self.dc.GetTextExtent(text_elements[i])
                pos_x += x

            # Update the offset.
            self.offset(y + 1)


    def generate(self, event):
        """Build the device context, add the background, and build the dialog.

        @param event:   The wx event.
        @type event:    wx event
        """

        ## Create the device context.
        #wx.BufferedPaintDC(self.window, self.buffer, wx.BUFFER_VIRTUAL_AREA)

        # Temporary fix for wxPython 2.9.3.1 suggested by Robin Dunn at http://groups.google.com/group/wxpython-users/browse_thread/thread/7dff3f5d7ca24985.
        dc = wx.PaintDC(self.window)
        self.window.PrepareDC(dc)
        dc.DrawBitmap(self.buffer, 0, 0)


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

        # Scrolling.
        y = y + self.window.GetViewStart()[1]*self.SCROLL_RATE

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
            self.virt_x = self.max_x
        else:
            self.virt_x = self.dim_x
        if self.max_y:
            self.virt_y = self.max_y
        else:
            self.virt_y = self.dim_y



class About_gui(About_base):
    """The about relax GUI dialog."""

    # The background colour.
    colour1 = 'white'

    # Dimensions.
    dim_x = 640
    dim_y = 480

    def build_widget(self):
        """Build the about dialog."""

        # The title.
        self.SetTitle("About relax GUI")

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
    dim_y = 700

    # Spacer size (px).
    border = 10

    def __init__(self, parent=None, id=-1, title="About relax"):
        """Build the dialog."""

        # Initialise the program information container.
        self.info = Info_box()

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
        self.draw_url(url_text=self.info.website, carriage_ret=True, centre=True)
        self.draw_icon()
        self.draw_desc_long()
        self.draw_licence()

        # Resize the window.
        dim_x = self.dim_x
        dim_y = self.offset() + self.border
        self.SetSize((dim_x, dim_y))
        self.window.SetVirtualSize((dim_x, dim_y))
        self.window.EnableScrolling(x_scrolling=False, y_scrolling=False)


    def draw_copyright(self):
        """Draw the copyright statements."""

        # Set the font.
        font = wx.Font(10, wx.FONTFAMILY_ROMAN, wx.NORMAL, wx.NORMAL)
        self.dc.SetFont(font)

        # The text extent.
        x1, y1 = self.dc.GetTextExtent(self.info.copyright[0])
        x2, y2 = self.dc.GetTextExtent(self.info.copyright[1])

        # Draw the text, with a starting spacer.
        self.dc.DrawText(self.info.copyright[0], (self.dim_x - x1)/2, self.offset(15))
        self.dc.DrawText(self.info.copyright[1], (self.dim_x - x2)/2, self.offset(y1+3))

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
        self.dc.DrawText(self.info.desc, (self.dim_x - x)/2, self.offset(15))

        # Add the text extent.
        self.offset(y)


    def draw_icon(self):
        """Draw the relax icon on the canvas."""

        # Add the relax logo.
        self.dc.DrawBitmap(wx.Bitmap(IMAGE_PATH+'ulysses_shadowless_400x168.png'), (self.dim_x - 400)/2, self.offset(20), True)

        # Add the bitmap width to the offset.
        self.offset(168)


    def draw_licence(self):
        """Draw the relax licence text."""

        self.draw_wrapped_text(self.info.licence, spacer=10)
