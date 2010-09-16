###############################################################################
#                                                                             #
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

# Module docstring.
"""The relax related references window."""

# Python module imports.
import webbrowser
import wx
import wx.html

# relax module imports.
from info import Info_box

# relax GUI module imports.
from gui_bieri.paths import IMAGE_PATH, BACKWARDS_ICON, FORWARDS_ICON

# HTML header.
HTML_HEADER = """\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
  <title>relax</title>
  <meta name="AUTHOR" content="Edward d'Auvergne"/>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
</head>

<body bgcolor="#e5feff">
"""

# HTML footer.
HTML_FOOTER = """\
</body>
</html>
"""


class References(wx.Frame):
    """The references window."""

    def __init__(self, parent):
        """Build the window.

        @param parent:  The parent wx object.
        @type parent:   wx object
        """

        # Init the base class.
        super(References, self).__init__(parent, -1, "relax references", style=wx.DEFAULT_FRAME_STYLE)

        # Set an initial window size.
        self.SetSize((800, 800))

        # Add a sizer box.
        box = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(box)

        # Add some buttons.
        #self.add_buttons(box)

        # The HTML window.
        self.html = RefWindow(self, -1, size=(500, -1))
        box.Add(self.html, 1, wx.GROW)

        # Catch clicks.
        self.Bind(wx.EVT_LEFT_DOWN, self.process_click)

        # Centre the window.
        self.Centre()

        # Show the front page.
        self.front_page()


    def process_click(self):
        pass

    def add_buttons(self, box):
        """Add forwards, backwards, and close buttons.

        @param box:     The box sizer element to pack the relax execution GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Create a horizontal box sizer to pack the buttons into.
        button_box = wx.BoxSizer(wx.HORIZONTAL)

        # Backwards button.
        button = wx.BitmapButton(self, -1, wx.Bitmap(BACKWARDS_ICON, wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
        button.SetSize(button.GetBestSize())
        self.Bind(wx.EVT_BUTTON, self.backwards, button)
        button_box.Add(button)

        # Forwards button.
        button = wx.BitmapButton(self, -1, wx.Bitmap(FORWARDS_ICON, wx.BITMAP_TYPE_ANY), style=wx.NO_BORDER)
        button.SetSize(button.GetBestSize())
        self.Bind(wx.EVT_BUTTON, self.forwards, button)
        button_box.Add(button)

        # Add the buttons.
        box.Add(button_box)


    def backwards(self, event):
        """Go backwards.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Go backwards.
        self.html.HistoryBack()


    def forwards(self, event):
        """Go forwards.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Go backwards.
        self.html.HistoryForward()


    def front_page(self):
        """The main reference page."""

        # Initialise the program information container.
        info = Info_box()

        # The HTML header.
        text = HTML_HEADER

        # The reference header.
        text = text + "<center>"
        text = text + "<img src=%s%s></img>" % (IMAGE_PATH, 'ulysses_shadowless_400x168.png')
        text = text + "<h1>relax references</h1>"
        text = text + "</center>"

        # Main refs.
        text = text + "<h2>The program relax</h2>"
        text = text + "<p>%s</p>" % info.bib['dAuvergneGooley08a'].cite_html()
        text = text + "<p>%s</p>" % info.bib['dAuvergneGooley08b'].cite_html()

        # GUI refs.
        text = text + "<h3><i>The relax GUI</i></h3>"
        text = text + "<p>%s</p>" % info.bib['Bieri10'].cite_html()

        # Model-free refs.
        text = text + "<h2>Model-free analysis</h2>"
        text = text + "<p>For a model-free analysis, all of the following should be cited!</p>"
        text = text + "<h3><i>Original Lipari-Szabo theory</i></h3>"
        text = text + "<p>%s</p>" % info.bib['LipariSzabo82a'].cite_html()
        text = text + "<p>%s</p>" % info.bib['LipariSzabo82b'].cite_html()
        text = text + "<h3><i>Extended model-free theory</i></h3>"
        text = text + "<p>%s</p>" % info.bib['Clore90'].cite_html()
        text = text + "<h3><i>Model-free model selection</i></h3>"
        text = text + "<p>%s</p>" % info.bib['dAuvergneGooley03'].cite_html()
        text = text + "<h3><i>Model-free model elimination</i></h3>"
        text = text + "<p>%s</p>" % info.bib['dAuvergneGooley06'].cite_html()
        text = text + "<h3><i>Model-free minimisation</i></h3>"
        text = text + "<p>%s</p>" % info.bib['dAuvergneGooley08a'].cite_html()
        text = text + "<h3><i>The new model-free analysis protocol</i></h3>"
        text = text + "<p>%s</p>" % info.bib['dAuvergneGooley07'].cite_html()
        text = text + "<p>%s</p>" % info.bib['dAuvergneGooley08b'].cite_html()
        text = text + "<h3><i>Comprehensive reference</i></h3>"
        text = text + "<p>This PhD thesis expands on all of the d'Auvergne and Gooley references and describes model-free analysis and the program relax in more detail:</p>"
        text = text + "<p>%s</p>" % info.bib['dAuvergne06'].cite_html()

        # The footer.
        text = text + HTML_FOOTER
        self.html.SetPage(text)



class RefWindow(wx.html.HtmlWindow):
    """New HTML window class to catch clicks on links and open in a browser."""

    def OnLinkClicked(self, url):
        """Redefine the link clicking behaviour."""

        # Open a new browser window instead.
        webbrowser.open(url.GetHref())
