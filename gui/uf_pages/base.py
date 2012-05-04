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
from gui.fonts import font
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.misc import str_to_gui
from gui.wizard import Wiz_page, Wiz_window


class UF_base:
    """User function GUI element base class."""

    def __init__(self, parent):
        """Set up the window.

        @param parent:      The parent window.
        @type parent:       wx.Window instance
        """

        # Store the arg.
        self.parent = parent


    def create_wizard(self, size_x=600, size_y=400, name=None, uf_page=None, apply_button=True, return_page=False):
        """Create and return the wizard window.

        @keyword size_x:        The width of the wizard.
        @type size_x:           int
        @keyword size_y:        The height of the wizard.
        @type size_y:           int
        @keyword name:          The name of the user function, such as 'deselect.all'.
        @type name:             str
        @keyword uf_page:       The user function page class.
        @type uf_page:          class
        @keyword apply_button:  A flag which if true will show the apply button for that page.  This will be passed to the wizard's add_page() method.
        @type apply_button:     bool
        @keyword return_page:   A flag which if True will cause the user function page to be returned.
        @type return_page:      bool
        @return:                The wizard dialog (and wizard page if the return flag is given).
        @rtype:                 gui.wizard.Wiz_window instance, wizard page instance
        """

        # Split the name.
        comps = split(name, '.')
        if len(comps) == 2:
            base = comps[0]
            fn = comps[1]
        else:
            base = None
            fn = comps[0]

        # Create the wizard dialog.
        wizard = Wiz_window(parent=self.parent, size_x=size_x, size_y=size_y, title=self.get_title(base=base, fn=fn))

        # Creat the page and add it to the wizard.
        page = uf_page(wizard)
        wizard.add_page(page, apply_button=apply_button)

        # Return the wizard and the page.
        if return_page:
            return wizard, page
        else:
            return wizard


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

    def __init__(self, parent, sync=False):
        """Set up the window.

        @param parent:      The parent class containing the GUI.
        @type parent:       class instance
        @keyword sync:      A flag which if True will call user functions via interpreter.apply and if False via interpreter.queue.
        @type sync:         bool
        """

        # Store the args.
        self.sync = sync

        # Default value data structure.
        self.defaults = {}

        # Yield to allow the cursor to be changed.
        wx.Yield()

        # Change the cursor to waiting.
        wx.BeginBusyCursor()

        # Get the user function class (or function).
        uf_class = getattr(interpreter._instance._interpreter, self.uf_path[0])

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

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()


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
        while True:
            if stripped_text[0] == "\n":
                stripped_text = stripped_text[1:]
            else:
                break

        # Remove the last character if a newline.
        while True:
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
                text_elements[-1].SetFont(font.subtitle)
            elif type == 'desc':
                text_elements[-1].SetFont(font.normal)
            elif type == 'table':
                text_elements[-1].SetFont(font.modern_small)

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


    def execute(self, uf, *args, **kwds):
        """Execute the user function, either asynchronously or synchronously.

        @param uf:      The user function as a string.
        @type uf:       str
        @param args:    The user function arguments.
        @type args:     any arguments
        @param kwds:    The user function keyword arguments.
        @type kwds:     any keyword arguments
        """

        # Synchronous execution.
        if self.sync:
            interpreter.apply(uf, *args, **kwds)

        # Asynchronous execution.
        else:
            interpreter.queue(uf, *args, **kwds)


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
