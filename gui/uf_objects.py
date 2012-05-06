###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
"""Module containing the special objects for auto-generating the GUI user functions and classes."""

# Python module imports.
from re import search
from string import split
from time import sleep
import wx
from wx.lib import scrolledpanel

# relax module imports.
from prompt.base_class import _strip_lead
from relax_errors import RelaxError
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI imports.
from gui.fonts import font
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.wizard import Wiz_page, Wiz_window


class Uf_object(object):
    """The object for auto-generating the GUI user functions."""

    def __call__(self, event):
        """Make the GUI user function executable.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Create the wizard dialog.
        wizard = Wiz_window(parent=self._parent, size_x=self._size[0], size_y=self._size[1], title=self._title)

        # Create the page.
        page = Uf_page(self._name, parent=wizard)

        # Add the page to the wizard.
        wizard.add_page(page, apply_button=self._apply_button)

        # Execute the wizard.
        wizard.run()


    def __init__(self, name, parent, title=None, size=None, apply_button=True):
        """Set up the object.

        @param name:            The name of the user function.
        @type name:             str
        @param parent:          The parent wx element.
        @type parent:           wx.Frame instance
        @keyword title:         The long title of the user function to set as the window title.
        @type title:            str
        @keyword size:          The window size.
        @type size:             tuple of int
        @keyword apply_button:  A flag specifying if the apply button should be shown or not.  This defaults to True.
        @type apply_button:     bool
        """

        # Store the args.
        self._name = name
        self._parent = parent
        self._title = title
        self._size = size
        self._apply_button = apply_button



class Uf_page(Wiz_page):
    """User function specific pages for the wizards."""

    # The path to the user function.
    uf_path = None

    def __init__(self, name, parent=None, sync=False):
        """Set up the window.

        @param name:        The name of the user function.
        @type name:         str
        @keyword parent:    The parent class containing the GUI.
        @type parent:       class instance
        @keyword sync:      A flag which if True will call user functions via interpreter.apply and if False via interpreter.queue.
        @type sync:         bool
        """

        # Store the args.
        self.name = name
        self.sync = sync

        # Default value data structure.
        self.defaults = {}

        # Yield to allow the cursor to be changed.
        wx.Yield()

        # Change the cursor to waiting.
        wx.BeginBusyCursor()

        # Get the user function data object.
        self.uf_data = uf_info.get_uf(name)

        # Set the wizard image.
        self.image_path = self.uf_data.wizard_image

        # Set the user function title.
        if self.uf_data.title_short != None:
            self.title = self.uf_data.title_short
        else:
            self.title = self.uf_data.title

        # Execute the base class method.
        super(Uf_page, self).__init__(parent)

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


    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Loop over the arguments.
        for i in range(len(self.uf_data.kargs)):
            # Alias.
            arg = self.uf_data.kargs[i]

            # The arg description formatting.
            desc = "The %s:" % arg['desc_short']

            # Special arg type:  file selection dialog.
            if arg['arg_type'] == 'file sel':
                self.element_file_sel(key=arg['name'], sizer=sizer, desc=desc, tooltip=arg['desc'], read_only=arg['wiz_read_only'])

            # Special arg type:  dir arg.
            elif arg['arg_type'] == 'dir':
                pass

            # Special arg type:  directory selection dialog.
            elif arg['arg_type'] == 'dir sel':
                self.element_dir_sel(key=arg['name'], sizer=sizer, desc=desc, tooltip=arg['desc'], read_only=arg['wiz_read_only'])

            # Value types.
            elif arg['py_type'] in ['float', 'int', 'str']:
                self.element_value(key=arg['name'], element_type=arg['wiz_element_type'], value_type=arg['py_type'], sizer=sizer, desc=desc, combo_choices=arg['wiz_combo_choices'], combo_data=arg['wiz_combo_data'], combo_default=arg['wiz_combo_default'], tooltip=arg['desc'], read_only=arg['wiz_read_only'])

            # Bool type.
            elif arg['py_type'] == 'bool':
                self.element_bool(key=arg['name'], element_type=arg['wiz_element_type'], sizer=sizer, desc=desc, tooltip=arg['desc'], default=arg['default'])

            # Sequence types.
            elif arg['py_type'] in ['float_list', 'int_list', 'num_list', 'str_list', 'float_tuple', 'int_tuple', 'num_tuple', 'str_tuple']:
                # The sequence type.
                if arg['py_type'] in ['float_list', 'int_list', 'num_list', 'str_list']:
                    seq_type = 'list'
                else:
                    seq_type = 'tuple'

                # The value type.
                if arg['py_type'] in ['float_list', 'float_tuple', 'num_list', 'num_tuple']:
                    value_type = 'float'
                elif arg['py_type'] in ['int_list', 'int_tuple']:
                    value_type = 'int'
                else:
                    value_type = 'str'

                self.element_sequence(key=arg['name'], element_type=arg['wiz_element_type'], seq_type=seq_type, value_type=value_type, sizer=sizer, desc=desc, combo_choices=arg['wiz_combo_choices'], combo_data=arg['wiz_combo_data'], combo_default=arg['wiz_combo_default'], combo_list_size=arg['wiz_combo_list_size'], tooltip=arg['desc'], read_only=arg['wiz_read_only'])

            # String list of lists.
            elif arg['py_type'] == 'str_list_of_lists':
                self.element_string_list_of_lists(key=arg['name'], titles=arg['list_titles'], sizer=sizer, desc=desc, tooltip=arg['desc'])

            # Unknown type.
            else:
                raise RelaxError("The Python object type '%s' cannot be handled." % arg['py_type'])


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
        if self.uf_data.desc != None:
            for element, type in self.process_doc([self.uf_data.title, self.uf_data.desc]):
                text_list.append([element, type])

        # Additional documentation.
        if self.uf_data.additional != None:
            for i in range(len(self.uf_data.additional)):
                for element, type in self.process_doc(self.uf_data.additional[i]):
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


    def on_display(self):
        """Clear and update the data if needed."""

        # Loop over the arguments.
        for i in range(len(self.uf_data.kargs)):
            # The argument name.
            name = self.uf_data.kargs[i]['name']

            # No iterator method for updating the list.
            iterator = self.uf_data.kargs[i]['wiz_combo_iter']
            if iterator == None:
                continue

            # Get the new choices and data.
            choices = []
            data = []
            for vals in iterator():
                if len(vals) == 2:
                    choices.append(vals[0])
                    data.append(vals[1])
                else:
                    choices.append(vals)
                    data.append(vals)

            # Reset.
            self.ResetChoices(name, combo_choices=choices, combo_data=data)


    def on_execute(self):
        """Execute the user function."""

        # Get the argument values.
        kargs = {}
        for i in range(len(self.uf_data.kargs)):
            # The argument name.
            name = self.uf_data.kargs[i]['name']

            # Store the value.
            kargs[name] = self.GetValue(name)

        # Display the relax controller, if asked.
        if self.uf_data.display:
            # Get the App.
            app = wx.GetApp()

            # First show the controller.
            app.gui.show_controller(None)

            # Go to the last line.
            app.gui.controller.log_panel.on_goto_end(None)

            # Wait a little while.
            sleep(0.5)

        # Execute the user function.
        self.execute(self.name, **kargs)

        # Bring the controller to the front.
        if self.uf_data.display:
            wx.CallAfter(app.gui.controller.Raise)


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



class Uf_storage(dict):
    """A singleton container for holding all the GUI user functions."""

    # Class variable for storing the class instance (for the singleton).
    _instance = None

    def __new__(self, *args, **kargs):
        """Replacement method for implementing the singleton design pattern."""

        # First instantiation.
        if self._instance is None:
            # Instantiate.
            self._instance = dict.__new__(self, *args, **kargs)

        # Already instantiated, so return the instance.
        return self._instance
