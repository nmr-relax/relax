###############################################################################
#                                                                             #
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
"""Base class module for the user function GUI elements."""

# Python module imports.
from re import search
from string import split
import wx
from wx.lib import scrolledpanel

# relax module imports.
from prompt.base_class import _strip_lead
from status import Status; status = Status()

# relax GUI imports.
from gui.misc import str_to_gui
from gui.wizard import Wiz_page


class UF_base:
    """User function GUI element base class."""

    def __init__(self, gui):
        """Set up the user function class."""

        # Store the args.
        self.gui = gui


    def get_title(self, base=None, fn=None):
        """Get the title for the wizard window from the user function documentation.

        @keyword base:  The name of the user function base class, if it exists.
        @type base:     str
        @keyword fn:    The name of the function of the base class, or the user function itself if there is no base class.
        @type fn:       str
        @return:        The title for the window.
        @rtype:         GUI str
        """

        # Prefix.
        title = 'relax:  '

        # Add the base.
        if base:
            title = "%s%s." % (title, base)

        # Add the function.
        title = "%s%s" % (title, fn)

        # Return the title as a GUI string.
        return str_to_gui(title)


class UF_page(Wiz_page):
    """User function specific pages for the wizards."""

    # The path to the user function.
    uf_path = None

    def __init__(self, parent, gui):
        """Set up the window.

        @param parent:      The parent class containing the GUI.
        @type parent:       class instance
        @param gui:         The GUI base object.
        @type gui:          wx.Frame instance
        """

        # Store the args.
        self.gui = gui

        # Get the user function class (or function).
        uf_class = getattr(self.gui.interpreter, self.uf_path[0])

        # Get the user function.
        if len(self.uf_path) == 1:
            self.uf = uf_class
        else:
            self.uf = getattr(uf_class, self.uf_path[1])

        # Set the user function title.
        if hasattr(self.uf, '_doc_title_short'):
            self.title = self.uf._doc_title_short
        else:
            self.title = self.uf._doc_title

        # Execute the base class method.
        super(UF_page, self).__init__(parent)


    def _format_text(self, text):
        """Format the text by stripping whitespace.

        @param text:    The text to strip.
        @type text:     str
        @return:        The stripped text.
        @rtype:         str
        """

        # First strip whitespace.
        stripped_text = _strip_lead(text)

        # Remove the first characters if newlines.
        while 1:
            if stripped_text[0] == "\n":
                stripped_text = stripped_text[1:]
            else:
                break

        # Remove the last character if a newline.
        while 1:
            if stripped_text[-1] == "\n":
                stripped_text = stripped_text[:-1]
            else:
                break

        # Return the text.
        return stripped_text


    def add_desc(self, sizer, max_y=220):
        """Add the description to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        @keyword max_y: The maximum height, in number of pixels, for the description.
        @type max_y:    int
        """

        # Initialise.
        spacing = 5

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)

        # Create a scrolled panel.
        panel = scrolledpanel.ScrolledPanel(self, -1, name="desc")

        # A sizer for the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Initialise the text elements.
        text_list = []

        # The description.
        if hasattr(self.uf, '_doc_desc'):
            for element, type in self.process_doc([self.uf._doc_title, self.uf._doc_desc]):
                text_list.append([element, type])

        # Additional documentation.
        if hasattr(self.uf, '_doc_additional'):
            for i in range(len(self.uf._doc_additional)):
                for element, type in self.process_doc(self.uf._doc_additional[i]):
                    text_list.append([element, type])

        # Loop over the elements.
        tot_x = 0
        tot_y = 0
        text_elements = []
        i = 0
        for text, type in text_list:
            # The text.
            text_elements.append(wx.StaticText(panel, -1, text, style=wx.TE_MULTILINE))

            # Format.
            if type == 'title':
                text_elements[-1].SetFont(self.gui.font_subtitle)
            elif type == 'desc':
                text_elements[-1].SetFont(self.gui.font_normal)
            elif type == 'table':
                text_elements[-1].SetFont(self.gui.font_8_modern)

            # Wrap the text.
            text_elements[-1].Wrap(self._main_size - 20)

            # The text size.
            x, y = text_elements[-1].GetSizeTuple()
            tot_x += x
            tot_y += y

            # Size for the spacing.
            tot_y += spacing
            if i != 0:
                tot_y += spacing

            # Increment.
            i += 1

        # Scrolling needed.
        if tot_y > max_y-10:
            # Set the panel size.
            panel.SetInitialSize((self._main_size, max_y))

        # No scrolling.
        else:
            # Rewrap the text.
            for i in range(len(text_elements)):
                text_elements[i].Wrap(self._main_size)

            # Set the panel size.
            panel.SetInitialSize((tot_x, tot_y))

        # Add the text.
        for i in range(len(text_elements)):
            # Initial spacing.
            if i != 0:
                panel_sizer.AddSpacer(spacing)

            # The text.
            panel_sizer.Add(text_elements[i], 0, wx.ALIGN_LEFT, 0)

            # Spacer after titles.
            if text_list[i][1] == 'title':
                panel_sizer.AddSpacer(spacing)

        # Set up and add the panel to the sizer.
        panel.SetSizer(panel_sizer)
        panel.SetAutoLayout(1)
        panel.SetupScrolling(scroll_x=False, scroll_y=True)
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND)

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)


    def on_completion(self):
        """Notify that the user function has completed."""

        # Notify.
        status.observers.gui_uf.notify()


    def process_doc(self, doc):
        """Process the documentation list.

        @param doc:     The documentation in the form of a list of the title and description.
        @type doc:      list of str
        """

        # The title.
        yield doc[0], 'title'

        # Split up the description.
        docstring_lines = split(doc[1], "\n")

        # Initialise.
        text = [""]
        type = ['desc']
        in_table = False

        # Loop over the lines of the docstring.
        for line in docstring_lines:
            # Start of the table.
            if not in_table and search('___', line):
                in_table = True
                text.append("")
                type.append("table")

            # Add the line to the text.
            text[-1] = "%s%s\n" % (text[-1], line)

            # End of the table.
            if in_table and search('^\\|_', line):
                in_table = False
                text.append("")
                type.append("desc")

        # Yield the bits.
        for i in range(len(text)):
            yield text[i], type[i]
