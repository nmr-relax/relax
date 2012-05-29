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
import arg_check
from graphics import fetch_icon
from relax_errors import AllRelaxErrors, RelaxError
from relax_string import strip_lead
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI imports.
from gui.components.free_file_format import Free_file_format
from gui.components.menu import build_menu_item
from gui.errors import gui_raise
from gui.fonts import font
from gui.input_elements.bool import Selector_bool
from gui.input_elements.dir import Selector_dir
from gui.input_elements.file import Selector_file
from gui.input_elements.sequence import Sequence
from gui.input_elements.sequence_2D import Sequence_2D
from gui.input_elements.spin_id import Spin_id
from gui.input_elements.value import Value
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.wizard import Wiz_page, Wiz_window


def build_uf_menus(parent=None, menubar=None):
    """Auto-generate the user function sub-menu.

    @keyword parent:    The parent window to bind the events to.
    @type parent:       wx instance
    @keyword menubar:   The menubar to attach the user function menus to.
    @type menubar:      wx.MenuBar instance
    @return:            The menu ID.
    @rtype:             int
    """

    # The user function menus.
    menu1 = wx.Menu()
    menu2 = wx.Menu()

    # The menu splitting.
    pattern = '^[a-m]'

    # Initialise some variables.
    class_list = []
    uf_store = Uf_storage()

    # Loop over the user functions.
    class_item = None
    menu = menu1
    menu_index = 0
    for name, data in uf_info.uf_loop():
        # Split up the name.
        if search('\.', name):
            class_name, uf_name = split(name, '.')
        else:
            class_name = None

        # Generate a sub menu.
        if class_name:
            if class_name not in class_list:
                # Add the last sub menu.
                if class_item != None:
                    menu.AppendItem(class_item)

                # Get the user function class data object.
                class_data = uf_info.get_class(class_name)

                # Create a unique ID.
                class_id = wx.NewId()

                # Create the menu entry.
                class_item = build_menu_item(menu, id=class_id, text=class_data.menu_text, icon=fetch_icon(class_data.gui_icon, size='16x16'))

                # Initialise the sub menu.
                sub_menu = wx.Menu()
                class_item.SetSubMenu(sub_menu)

                # Add the class name to the list to block further sub menu creation.
                class_list.append(class_name)

            # Create the user function menu entry.
            uf_id = wx.NewId()
            sub_menu.AppendItem(build_menu_item(sub_menu, id=uf_id, text=data.menu_text, icon=fetch_icon(data.gui_icon, size='16x16')))

        # No sub menu.
        else:
            # Add the last sub menu.
            if class_item != None:
                menu.AppendItem(class_item)
                class_item = None

            # The menu item.
            uf_id = wx.NewId()
            menu.AppendItem(build_menu_item(menu, id=uf_id, text=data.menu_text, icon=fetch_icon(data.gui_icon, size='16x16')))

        # New menu.
        if menu_index == 0 and not search(pattern, name):
            menu = menu2
            menu_index = 1

        # Bind the menu item to the parent.
        parent.Bind(wx.EVT_MENU, uf_store[name], id=uf_id)

    # Add the very last sub menu.
    if class_item != None:
        menu.AppendItem(class_item)

    # Add the user function menu to the menu bar.
    title1 = "&User functions (a-m)"
    title2 = "&User functions (n-z)"
    menubar.Append(menu1, title1)
    menubar.Append(menu2, title2)

    # Return the menu IDs.
    return [menubar.FindMenu(title1), menubar.FindMenu(title2)]



class Uf_object(object):
    """The object for auto-generating the GUI user functions."""

    def __call__(self, event=None, wx_parent=None, wx_wizard_run=True, **kwds):
        """Make the GUI user function executable.

        All keyword args, apart from 'event', 'wx_parent' and 'wx_wizard_run' will be assumed to be user function arguments and the Uf_page.SetValue() method of the page will be used to set the GUI arg elements to the values supplied.


        @keyword event:         The wx event.
        @type event:            wx event or None
        @keyword wx_parent:     The parent wx object to associate the user function wizard to.
        @type wx_parent:        wx object
        @keyword wx_wizard_run: A flag which if True will call the wizard run() method.
        @type wx_wizard_run:    bool
        """

        # Create a new wizard if needed (checking that the parent of an old wizard is not the same).
        if self.wizard == None or (wx_parent != None and wx_parent != self.wizard.GetParent()) or self.wizard._pages[0] == None:
            self.create_wizard(wx_parent)

        # Otherwise reset the wizard.
        else:
            self.wizard.reset()

        # Update all of the user function argument choices (ComboBoxes) to be current.
        self.page.update_args()

        # Loop over the keyword args, using the Uf_page.SetValue() method to set the user function argument GUI element values.
        for key in kwds:
            self.page.SetValue(key, kwds[key])

        # Execute the wizard when asked.
        if wx_wizard_run:
            self.wizard.run()


    def __init__(self, name, title=None, size=None, height_desc=None, apply_button=True, sync=False):
        """Set up the object.

        @param name:            The name of the user function.
        @type name:             str
        @keyword title:         The long title of the user function to set as the window title.
        @type title:            str
        @keyword size:          The window size.
        @type size:             tuple of int
        @keyword height_desc:   The height in pixels of the description part of the wizard.
        @type height_desc:      int or None
        @keyword apply_button:  A flag specifying if the apply button should be shown or not.  This defaults to True.
        @type apply_button:     bool
        @keyword sync:          A flag which if True will call user functions via interpreter.apply and if False via interpreter.queue.
        @type sync:             bool
        """

        # Store the args.
        self._name = name
        self._title = title
        self._size = size
        self._height_desc = height_desc
        self._apply_button = apply_button
        self._sync = sync

        # Initialise the wizard storage.
        self.wizard = None


    def create_page(self, wizard=None, sync=False):
        """Create the user function wizard page GUI object.

        @keyword wizard:    The parent wizard.
        @type wizard:       Wiz_window instance
        @keyword sync:      A flag which if True will call user functions via interpreter.apply and if False via interpreter.queue.
        @type sync:         bool
        @return:            The user function page object.
        @rtype:             Uf_page instance
        """

        # Initialise and return the page.
        return Uf_page(self._name, parent=wizard, height_desc=self._height_desc, sync=self._sync)


    def create_wizard(self, parent=None):
        """Create the user function wizard GUI object, with embedded wizard page.

        @keyword parent:    The parent wx window.
        @type parent:       wx.Window instance
        """

        # The parent object defaults to the main relax window.
        if parent == None:
            app = wx.GetApp()
            parent = app.gui

        # Create the wizard dialog.
        self.wizard = Wiz_window(parent=parent, size_x=self._size[0], size_y=self._size[1], title=self._title)

        # Create the page.
        self.page = self.create_page(self.wizard, sync=self._sync)

        # For an update of the argument data.
        self.page.update_args()

        # Add the page to the wizard.
        self.wizard.add_page(self.page, apply_button=self._apply_button)



class Uf_page(Wiz_page):
    """User function specific pages for the wizards."""

    def __init__(self, name, parent=None, height_desc=220, sync=False):
        """Set up the window.

        @param name:            The name of the user function.
        @type name:             str
        @keyword parent:        The parent class containing the GUI.
        @type parent:           class instance
        @keyword height_desc:   The height in pixels of the description part of the wizard.
        @type height_desc:      int or None
        @keyword sync:          A flag which if True will call user functions via interpreter.apply and if False via interpreter.queue.
        @type sync:             bool
        """

        # Store the args.
        self.name = name
        self.sync = sync

        # Storage of the user function argument elements.
        self.uf_args = {}

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
        super(Uf_page, self).__init__(parent, height_desc=height_desc)

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
        stripped_text = strip_lead(text)

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


    def _intro_text(self, keys, values, prompt=True):
        """Build and return the user function intro text.

        @param keys:        The user function keys.
        @type keys:         list of str
        @param values:      The values corresponding to the keys.
        @type values:       list
        @keyword prompt:    A flag which if True will cause the prompt text to be included.
        @type prompt:       bool
        @return:            The user function intro text.
        @rtype:             str
        """

        # Initialise.
        text = ""

        # The prompt.
        if prompt:
            text += status.ps3

        # The user function name.
        text += "%s(" % self.name

        # The keyword args.
        for i in range(len(keys)):
            # Comma separation.
            if i >= 1:
                text += ", "

            # Add the arg.
            text += "%s=%s" % (keys[i], repr(values[i]))

        # The end.
        text += ")"

        # Return the text.
        return text


    def Clear(self, key):
        """Special wizard method for clearing the value of the GUI element corresponding to the key.

        @param key:     The key corresponding to the desired GUI element.
        @type key:      str
        """

        # Call the argument element's method.
        self.uf_args[key].Clear()


    def GetValue(self, key):
        """Special wizard method for getting the value of the GUI element corresponding to the key.

        @param key:     The key corresponding to the desired GUI element.
        @type key:      str
        @return:        The value that the specific GUI element's GetValue() method returns.
        @rtype:         unknown
        """

        # The key is not set, so assume this is a hidden argument.
        if key not in self.uf_args.keys():
            return None

        # Call the argument element's method.
        return self.uf_args[key].GetValue()


    def SetValue(self, key, value):
        """Special wizard method for setting the value of the GUI element corresponding to the key.

        @param key:     The key corresponding to the desired GUI element.
        @type key:      str
        @param value:   The value that the specific GUI element's SetValue() method expects.
        @type value:    unknown
        """

        # Find the argument.
        arg = None
        for i in range(len(self.uf_data.kargs)):
            if self.uf_data.kargs[i]['name'] == key:
                arg = self.uf_data.kargs[i]

        # No match.
        if arg == None:
            raise RelaxError("The key '%s' is unknown." % key)

        # Handle the free file format args (for external control, i.e. via the test suite).
        if 'free_file_format' in self.uf_args and key in ['spin_id_col', 'mol_name_col', 'res_num_col', 'res_name_col', 'spin_num_col', 'spin_name_col', 'data_col', 'error_col', 'sep']:
            self.uf_args['free_file_format'].SetValue(key, value)

        # Skip functions and function args, as these are not supported in the GUI.
        elif arg['arg_type'] in ['func', 'func args']:
            pass

        # Call the argument element's method.
        else:
            self.uf_args[key].SetValue(value)


    def UpdateChoices(self, key, combo_choices=None, combo_data=None, combo_default=None):
        """Special user function page method for updating the list of choices in a ComboBox type element.

        @param key:             The key corresponding to the desired GUI element.
        @type key:              str
        @keyword combo_choices: The list of choices to present to the user.  This is only used if the element_type is set to 'combo'.
        @type combo_choices:    list of str
        @keyword combo_data:    The data returned by a call to GetValue().  This is only used if the element_type is set to 'combo'.  If supplied, it should be the same length at the combo_choices list.  If not supplied, the combo_choices list will be used for the returned data.
        @type combo_data:       list
        @keyword combo_default: The default value of the ComboBox.  This is only used if the element_type is set to 'combo'.
        @type combo_default:    str or None
        """

        # Call the argument element's method.
        self.uf_args[key].UpdateChoices(combo_choices=combo_choices, combo_data=combo_data, combo_default=combo_default)


    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Initialise the free format file settings flag.
        free_format = False
        free_format_data = False

        # Loop over the arguments.
        for i in range(len(self.uf_data.kargs)):
            # Alias.
            arg = self.uf_data.kargs[i]

            # The arg description formatting.
            desc = "The %s:" % arg['desc_short']

            # Special arg type:  file selection dialog.
            if arg['arg_type'] == 'file sel':
                self.uf_args[arg['name']] = Selector_file(name=arg['name'], parent=self, default=arg['default'], sizer=sizer, desc=desc, wildcard=arg['wiz_filesel_wildcard'], style=arg['wiz_filesel_style'], tooltip=arg['desc'], divider=self._div_left, height_element=self.height_element, read_only=arg['wiz_read_only'])

            # Special arg type:  dir arg.
            elif arg['arg_type'] == 'dir':
                pass

            # Special arg type:  directory selection dialog.
            elif arg['arg_type'] == 'dir sel':
                self.uf_args[arg['name']] = Selector_dir(name=arg['name'], parent=self, default=arg['default'], sizer=sizer, desc=desc, style=arg['wiz_dirsel_style'], tooltip=arg['desc'], divider=self._div_left, height_element=self.height_element, read_only=arg['wiz_read_only'])

            # Special arg type:  free format file settings.
            elif arg['arg_type'] == 'free format':
                # Switch the flags.
                free_format = True
                if arg['name'] == 'data_col':
                    free_format_data = True

            # Special arg type:  functions and their arguments!
            elif arg['arg_type'] in ['func', 'func args']:
                pass

            # Special arg type:  spin IDs.
            elif arg['arg_type'] in ['spin ID']:
                self.uf_args[arg['name']] = Spin_id(name=arg['name'], parent=self, default=arg['default'], element_type=arg['wiz_element_type'], sizer=sizer, desc=desc, combo_choices=arg['wiz_combo_choices'], combo_data=arg['wiz_combo_data'], tooltip=arg['desc'], divider=self._div_left, height_element=self.height_element, can_be_none=arg['can_be_none'])

            # Value types.
            elif arg['py_type'] in ['float', 'int', 'num', 'str']:
                self.uf_args[arg['name']] = Value(name=arg['name'], parent=self, default=arg['default'], element_type=arg['wiz_element_type'], value_type=arg['py_type'], min=arg['min'], max=arg['max'], sizer=sizer, desc=desc, combo_choices=arg['wiz_combo_choices'], combo_data=arg['wiz_combo_data'], tooltip=arg['desc'], divider=self._div_left, height_element=self.height_element, read_only=arg['wiz_read_only'], can_be_none=arg['can_be_none'])

            # Bool type.
            elif arg['py_type'] == 'bool':
                self.uf_args[arg['name']] = Selector_bool(name=arg['name'], parent=self, element_type=arg['wiz_element_type'], sizer=sizer, desc=desc, tooltip=arg['desc'], default=arg['default'], divider=self._div_left, height_element=self.height_element)

            # Sequence types.
            elif arg['py_type'] in ['float_list', 'int_list', 'num_list', 'str_list', 'float_tuple', 'int_tuple', 'num_tuple', 'str_tuple', 'float_array', 'int_array', 'float_or_float_list', 'int_or_int_list', 'num_or_num_list', 'str_or_str_list', 'float_or_float_tuple', 'int_or_int_tuple', 'num_or_num_tuple', 'str_or_str_tuple', 'val_or_list']:
                # The sequence type.
                if arg['py_type'] in ['float_list', 'int_list', 'num_list', 'str_list', 'float_array', 'int_array', 'float_or_float_list', 'int_or_int_list', 'num_or_num_list', 'str_or_str_list', 'val_or_list']:
                    seq_type = 'list'
                else:
                    seq_type = 'tuple'

                # The value type.
                if arg['py_type'] in ['float_list', 'num_list', 'float_tuple', 'num_tuple', 'float_array', 'float_or_float_list', 'num_or_num_list', 'float_or_float_tuple', 'num_or_num_tuple']:
                    value_type = 'float'
                elif arg['py_type'] in ['int_list', 'int_tuple', 'int_array', 'int_or_int_list', 'int_or_int_tuple']:
                    value_type = 'int'
                elif arg['py_type'] in ['str_list', 'str_tuple', 'str_array', 'str_or_str_list', 'str_or_str_tuple']:
                    value_type = 'str'
                else:
                    value_type = None

                # Single values.
                single_value = False
                if arg['py_type'] in ['float_or_float_list', 'int_or_int_list', 'num_or_num_list', 'str_or_str_list', 'float_or_float_tuple', 'int_or_int_tuple', 'num_or_num_tuple', 'str_or_str_tuple', 'val_or_list']:
                    single_value = True

                # Dimensions.
                dim = None
                if isinstance(arg['dim'], int):
                    dim = arg['dim']

                self.uf_args[arg['name']] = Sequence(name=arg['name'], parent=self, default=arg['default'], element_type=arg['wiz_element_type'], seq_type=seq_type, value_type=value_type, dim=dim, min=arg['min'], max=arg['max'], sizer=sizer, desc=desc, combo_choices=arg['wiz_combo_choices'], combo_data=arg['wiz_combo_data'], combo_list_min=arg['wiz_combo_list_min'], tooltip=arg['desc'], single_value=single_value, divider=self._div_left, height_element=self.height_element, read_only=arg['wiz_read_only'], can_be_none=arg['can_be_none'])

            # 2D sequence types.
            elif arg['py_type'] in ['float_list_of_lists', 'int_list_of_lists', 'num_list_of_lists', 'str_list_of_lists', 'float_tuple_of_tuples', 'int_tuple_of_tuples', 'num_tuple_of_tuples', 'str_tuple_of_tuples', 'float_matrix', 'int_matrix']:
                # The sequence type.
                if arg['py_type'] in ['float_list_of_lists', 'int_list_of_lists', 'num_list_of_lists', 'str_list_of_lists', 'float_matrix', 'int_matrix']:
                    seq_type = 'list'
                else:
                    seq_type = 'tuple'

                # The value type.
                if arg['py_type'] in ['float_list_of_lists', 'float_tuple_of_tuples', 'num_list_of_lists', 'num_tuple_of_tuples', 'float_matrix']:
                    value_type = 'float'
                elif arg['py_type'] in ['int_list_of_lists', 'int_tuple_of_tuples', 'int_matrix']:
                    value_type = 'int'
                else:
                    value_type = 'str'

                self.uf_args[arg['name']] = Sequence_2D(name=arg['name'], parent=self, default=arg['default'], sizer=sizer, element_type=arg['wiz_element_type'], seq_type=seq_type, value_type=value_type, dim=arg['dim'], min=arg['min'], max=arg['max'], titles=arg['list_titles'], desc=desc, combo_choices=arg['wiz_combo_choices'], combo_data=arg['wiz_combo_data'], combo_list_min=arg['wiz_combo_list_min'], tooltip=arg['desc'], divider=self._div_left, height_element=self.height_element, read_only=arg['wiz_read_only'], can_be_none=arg['can_be_none'])

            # Unknown type.
            else:
                raise RelaxError("The Python object type '%s' cannot be handled." % arg['py_type'])

        # Add the free format element.
        if free_format:
            self.uf_args['free_file_format'] = Free_file_format(sizer, parent=self, data_cols=free_format_data, padding=3, spacer=0)


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
        if self.sync or status.gui_uf_force_sync:
            interpreter.apply(uf, *args, **kwds)

        # Asynchronous execution.
        else:
            interpreter.queue(uf, *args, **kwds)


    def on_completion(self):
        """Update the argument GUI elements if needed."""

        # Update the args.
        self.update_args()


    def on_display(self):
        """Clear and update the data if needed."""

        # Update the args.
        self.update_args()


    def on_execute(self):
        """Execute the user function."""

        # Get the argument values.
        kargs = {}
        for i in range(len(self.uf_data.kargs)):
            # The argument name.
            name = self.uf_data.kargs[i]['name']

            # Store the value.
            kargs[name] = self.GetValue(name)

            # Skip execution when a Combo_list does not have enough elements.
            if self.uf_data.kargs[i]['wiz_combo_list_min'] != None and kargs[name] == None:
                return

        # Handle the free file format args.
        if 'free_file_format' in self.uf_args:
            kargs.update(self.uf_args['free_file_format'].GetValue())

        # Display the relax controller, if asked.
        if self.uf_data.display:
            # Get the App.
            app = wx.GetApp()

            # First show the controller.
            app.gui.show_controller(None)

            # Go to the last line.
            app.gui.controller.log_panel.on_goto_end(None)

        # The user function intro text.
        if status.uf_intro:
            # Convert the keys and values.
            keys = []
            values = []
            for i in range(len(self.uf_data.kargs)):
                keys.append(self.uf_data.kargs[i]['name'])
                values.append(kargs[self.uf_data.kargs[i]['name']])

            # The printout.
            print(self._intro_text(keys, values))

        # Execute the user function.
        self.execute(self.name, **kargs)

        # Bring the controller to the front.
        if status.show_gui and self.uf_data.display:
            wx.CallAfter(app.gui.controller.Raise)


    def process_doc(self, doc):
        """Process the documentation list.

        @param doc:     The documentation in the form of a list of the title and description.
        @type doc:      list of str
        """

        # The title.
        yield doc[0], 'title'

        # Strip the leading whitespace, if needed.
        doc[1] = strip_lead(doc[1])

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
            if in_table and line == '':
                in_table = False
                text.append("")
                type.append("desc")

        # Yield the bits.
        for i in range(len(text)):
            yield text[i], type[i]


    def update_args(self):
        # Loop over the arguments.
        for i in range(len(self.uf_data.kargs)):
            # The argument name.
            name = self.uf_data.kargs[i]['name']

            # No iterator method for updating the list.
            iterator = self.uf_data.kargs[i]['wiz_combo_iter']
            if iterator == None:
                continue

            # Get the new choices and data (in a safe way).
            try:
                choices = []
                data = []
                for vals in iterator():
                    if arg_check.is_tuple(vals, size=2, raise_error=False):
                        choices.append(vals[0])
                        data.append(vals[1])
                    else:
                        choices.append(vals)
                        data.append(vals)

            # Catch all RelaxErrors.
            except AllRelaxErrors, instance:
                # Signal the failure to the wizard.
                self.setup_fail = True

                # Display a dialog with the error.
                gui_raise(instance)

                # Return as a failure.
                return False

            # Update the GUI element.
            self.UpdateChoices(name, combo_choices=choices, combo_data=data)



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

            # Generate the user functions.
            for name, data in uf_info.uf_loop():
                # Generate a new container.
                obj = Uf_object(name, title=data.title, size=data.wizard_size, height_desc=data.wizard_height_desc, apply_button=data.wizard_apply_button, sync=data.gui_sync)

                # Store it.
                self._instance[name] = obj

        # Already instantiated, so return the instance.
        return self._instance
