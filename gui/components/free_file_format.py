###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
import wx
from wx.lib import buttons

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from graphics import IMAGE_PATH, fetch_icon
from gui.fonts import font
from gui.icons import relax_icons
from gui.input_elements.value import Value
from gui.message import Question
from gui.misc import bitmap_setup
from gui.string_conv import gui_to_int, gui_to_str, int_to_gui, str_to_gui
from gui.wizards.wiz_objects import Wiz_page
from lib.errors import RelaxError
from status import Status; status = Status()


class Free_file_format:
    """GUI element for the free file format.

    This is used for specifying the columns used for the molecule name, residue name and number, spin name and number and data and error columns.
    """

    size_square_button = (33, 33)

    def __init__(self, parent=None, element_type='default', sizer=None, divider=None, padding=10, spacer=3, height_element=27, data_cols=False, save=True, reset=True):
        """Build the free format file settings widget.

        @keyword parent:            The parent wx GUI element.
        @type parent:               wx object
        @keyword element_type:      The type of GUI element to create.  The value of 'default' creates the large GUI element with a row for each column and for the separator.  If 'mini' is supplied, the single row element will be used.
        @type element_type:         str
        @keyword sizer:             The sizer to put the GUI element into.
        @type sizer:                wx.Sizer instance
        @keyword divider:           The position of the divider.
        @type divider:              int
        @keyword padding:           The size of the padding between the wx.StaticBoxSizer border and the internal elements, in pixels.
        @type padding:              int
        @keyword spacer:            The horizontal spacing between the elements, in pixels.
        @type spacer:               int
        @keyword height_element:    The height in pixels of the GUI element.  This is only used for the mini format.
        @type height_element:       int
        @keyword data_cols:         A flag which if True causes the data and error column elements to be displayed.
        @type data_cols:            bool
        @keyword save:              A flag which if True will cause the save button to be displayed.
        @type save:                 bool
        @keyword reset:             A flag which if True will cause the reset button to be displayed.
        @type reset:                bool
        """

        # Store the args.
        self.parent = parent
        self.sizer = sizer
        self.divider = divider
        self.element_type = element_type
        self.padding = padding
        self.spacer = spacer
        self.height_element = height_element
        self.data_cols = data_cols
        self.save_flag = save
        self.reset_flag = reset

        # The large GUI element.
        if self.element_type == 'default':
            self._build_default()

        # The mini GUI element.
        elif self.element_type == 'mini':
            self._build_mini()

        # Unknown type.
        else:
            raise RelaxError("Unknown free file format element type '%s'." % element_type)


    def _build_default(self):
        """Build the default GUI element."""

        # A static box to hold all the widgets.
        box = wx.StaticBox(self.parent, -1, "The free file format settings:")
        box.SetFont(font.subtitle)

        # Init.
        main_sizer = wx.StaticBoxSizer(box, wx.HORIZONTAL)
        field_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer = wx.BoxSizer(wx.VERTICAL)

        # The border of the widget.
        border = wx.BoxSizer()

        # Place the box sizer inside the border.
        border.Add(main_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add to the main sizer (followed by stretchable spacing).
        self.sizer.Add(border, 0, wx.EXPAND)
        self.sizer.AddStretchSpacer()

        # Calculate the divider position.
        divider = self.parent._div_left - border.GetMinSize()[0] / 2 - self.padding

        # The columns.
        self.spin_id_col = Value(name='spin_id_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="spin ID column", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)
        self.mol_name_col = Value(name='mol_name_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="Molecule name column:", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)
        self.res_num_col = Value(name='res_num_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="Residue number column:", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)
        self.res_name_col = Value(name='res_name_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="Residue name column:", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)
        self.spin_num_col = Value(name='spin_num_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="Spin number column:", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)
        self.spin_name_col = Value(name='spin_name_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="Spin name column:", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)
        if self.data_cols:
            self.data_col = Value(name='data_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="Data column:", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)
            self.error_col = Value(name='error_col', parent=self.parent, value_type='int', sizer=field_sizer, desc="Error column:", divider=divider, padding=self.padding, spacer=self.spacer, can_be_none=True)

        # The column separator.
        self.sep = Value(name='sep', parent=self.parent, element_type='combo', value_type='str', sizer=field_sizer, desc="Column separator:", combo_choices=["white space", ",", ";", ":", ""], divider=divider, padding=self.padding, spacer=self.spacer, read_only=False, can_be_none=True)

        # Add the field sizer to the main sizer.
        main_sizer.Add(field_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Set the values.
        self.set_vals()

        # Buttons!
        if self.save_flag or self.reset_flag:
            # Add a save button.
            if self.save_flag:
                # Build the button.
                button = buttons.ThemedGenBitmapTextButton(self.parent, -1, None, "")
                button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.document-save', "22x22"), wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Save the free file format settings within the relax data store.")
                button.SetMinSize(self.size_square_button)

                # Add the button.
                button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

                # Padding.
                button_sizer.AddSpacer(self.padding)

                # Bind the click event.
                self.parent.Bind(wx.EVT_BUTTON, self.save, button)

            # Add a reset button.
            if self.reset_flag:
                # Build the button.
                button = buttons.ThemedGenBitmapTextButton(self.parent, -1, None, "")
                button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.edit-delete', "22x22"), wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Reset the free file format settings to the original values.")
                button.SetMinSize(self.size_square_button)

                # Add the button.
                button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

                # Bind the click event.
                self.parent.Bind(wx.EVT_BUTTON, self.reset, button)

            # Add the button sizer to the widget (with spacing).
            main_sizer.AddSpacer(self.padding)
            main_sizer.Add(button_sizer, 0, wx.ALL, 0)


    def _build_mini(self):
        """Build the mini GUI element."""

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(self.padding)

        # The description.
        text = wx.StaticText(self.parent, -1, "Free format file settings", style=wx.ALIGN_LEFT)
        text.SetFont(font.normal)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not self.divider:
            raise RelaxError("The divider position has not been supplied.")

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((self.divider - x, 0))

        # Initialise the text input field.
        self.field = wx.TextCtrl(self.parent, -1, '')
        self.field.SetEditable(False)
        colour = self.parent.GetBackgroundColour()
        self.field.SetOwnBackgroundColour(colour)
        self.field.SetMinSize((50, self.height_element))
        self.field.SetFont(font.normal)
        sub_sizer.Add(self.field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The edit button.
        button = wx.BitmapButton(self.parent, -1, wx.Bitmap(fetch_icon("oxygen.actions.document-properties"), wx.BITMAP_TYPE_ANY))
        button.SetMinSize((self.height_element, self.height_element))
        button.SetToolTipString("Open the free file format editing window.")
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        self.parent.Bind(wx.EVT_BUTTON, self.open_window, button)

        # Right padding.
        sub_sizer.AddSpacer(self.padding)

        # Add to the main sizer.
        self.sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if self.spacer == None:
            self.sizer.AddStretchSpacer()
        else:
            self.sizer.AddSpacer(self.spacer)

        # Tooltip.
        tooltip = "The free file format settings."
        text.SetToolTipString(tooltip)
        self.field.SetToolTipString(tooltip)

        # Set the values.
        self.set_vals()


    def GetValue(self):
        """Return the free file format settings as a keyword dictionary.

        @return:    The dictionary of free file format settings.
        @rtype:     dict
        """

        # Initialise.
        settings = {}

        # The default GUI element.
        if self.element_type == 'default':
            # Get the column numbers.
            settings['spin_id_col'] =   gui_to_int(self.spin_id_col.GetValue())
            settings['mol_name_col'] =  gui_to_int(self.mol_name_col.GetValue())
            settings['res_num_col'] =   gui_to_int(self.res_num_col.GetValue())
            settings['res_name_col'] =  gui_to_int(self.res_name_col.GetValue())
            settings['spin_num_col'] =  gui_to_int(self.spin_num_col.GetValue())
            settings['spin_name_col'] = gui_to_int(self.spin_name_col.GetValue())
            if self.data_cols:
                settings['data_col'] =  gui_to_int(self.data_col.GetValue())
                settings['error_col'] = gui_to_int(self.error_col.GetValue())

            # The column separator.
            settings['sep'] = str(self.sep.GetValue())
            if settings['sep'] == 'white space':
                settings['sep'] = None

        # The mini GUI element.
        elif self.element_type == 'mini':
            # Convert the values.
            values = self.from_string(string=gui_to_str(self.field.GetValue()))

            # Store them.
            settings['spin_id_col'] = values[0]
            settings['mol_name_col'] = values[1]
            settings['res_num_col'] = values[2]
            settings['res_name_col'] = values[3]
            settings['spin_num_col'] = values[4]
            settings['spin_name_col'] = values[5]
            if self.data_cols:
                settings['data_col'] = values[6]
                settings['error_col'] = values[7]
                settings['sep'] = values[8]
            else:
                settings['sep'] = values[6]

        # Return the settings.
        return settings


    def SetValue(self, key, value):
        """Special method for setting the value of the GUI element corresponding to the key.

        @param key:     The key corresponding to the desired GUI element.  This can be one of ['spin_id_col', 'mol_name_col', 'res_num_col', 'res_name_col', 'spin_num_col', 'spin_name_col', 'data_col', 'error_col', 'sep'].
        @type key:      str
        @param value:   The value that the specific GUI element's SetValue() method expects.
        @type value:    unknown
        """

        # The default GUI element.
        if self.element_type == 'default':
            # Get the element.
            obj = getattr(self, key)

            # Convert the data.
            if key == 'sep':
                value = str_to_gui(value)
            else:
                value = int_to_gui(value)

            # Set the value.
            obj.SetValue(value)

        # The mini GUI element.
        elif self.element_type == 'mini':
            # Get the current values.
            settings = self.GetValue()

            # Replace the value.
            settings[key] = value

            # Set the values.
            if self.data_cols:
                string = self.to_string(spin_id_col=settings['spin_id_col'], mol_name_col=settings['mol_name_col'], res_num_col=settings['res_num_col'], res_name_col=settings['res_name_col'], spin_num_col=settings['spin_num_col'], spin_name_col=settings['spin_name_col'], data_col=settings['data_col'], error_col=settings['error_col'], sep=settings['sep'])
            else:
                string = self.to_string(spin_id_col=settings['spin_id_col'], mol_name_col=settings['mol_name_col'], res_num_col=settings['res_num_col'], res_name_col=settings['res_name_col'], spin_num_col=settings['spin_num_col'], spin_name_col=settings['spin_name_col'], sep=settings['sep'])
            self.field.SetValue(str_to_gui(string))


    def from_string(self, string=None):
        """Convert the free file format variables to string format.

        @keyword string:        The string to convert.
        @type string:           str
        @return:                The spin ID column, molecule name column, residue number column, residue number column, spin number column, spin name column, data column (if active), error column (if active), and column separator.
        @rtype:                 list of str or None
        """

        # The number of elements.
        num = 6
        if self.data_cols:
            num = 8

        # Nothing.
        if string == None:
            return [None] * num

        # Store the columns.
        values = []
        temp = string.split(',')
        for i in range(num):
            # No value.
            if temp[i] in ['None', ' None']:
                values.append(None)

            # Integer.
            else:
                values.append(int(temp[i]))

        # Handle the separator.
        temp = string.split('\'')
        sep = temp[-2]
        if sep == "white space":
            values.append(None)
        else:
            values.append(sep)

        # Return the values.
        return values


    def open_window(self, event):
        """Open the free file format editing window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the window.
        win = Free_file_format_window()

        # Show the window.
        if status.show_gui:
            win.ShowModal()

        # Set the values.
        self.set_vals()


    def reset(self, event):
        """Reset the free file format widget contents to the original values.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask a question.
        if status.show_gui and Question('Would you really like to reset the free file format settings?', parent=self.parent).ShowModal() == wx.ID_NO:
            return

        # First reset.
        ds.relax_gui.free_file_format.reset()

        # Then update the values.
        self.set_vals()


    def save(self, event):
        """Save the free file format widget contents into the relax data store.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The default GUI element.
        if self.element_type == 'default':
            # Get the column numbers.
            ds.relax_gui.free_file_format.spin_id_col =   gui_to_int(self.spin_id_col.GetValue())
            ds.relax_gui.free_file_format.mol_name_col =  gui_to_int(self.mol_name_col.GetValue())
            ds.relax_gui.free_file_format.res_num_col =   gui_to_int(self.res_num_col.GetValue())
            ds.relax_gui.free_file_format.res_name_col =  gui_to_int(self.res_name_col.GetValue())
            ds.relax_gui.free_file_format.spin_num_col =  gui_to_int(self.spin_num_col.GetValue())
            ds.relax_gui.free_file_format.spin_name_col = gui_to_int(self.spin_name_col.GetValue())

            # The data and error.
            if hasattr(self, 'data_col'):
                ds.relax_gui.free_file_format.data_col = gui_to_int(self.data_col.GetValue())
            if hasattr(self, 'error_col'):
                ds.relax_gui.free_file_format.error_col = gui_to_int(self.error_col.GetValue())

            # The column separator.
            ds.relax_gui.free_file_format.sep = str(self.sep.GetValue())
            if ds.relax_gui.free_file_format.sep == 'white space':
                ds.relax_gui.free_file_format.sep = None

        # The mini GUI element.
        elif self.element_type == 'mini':
            # Get the current values.
            settings = self.GetValue()

            # Store the values.
            ds.relax_gui.free_file_format.spin_id_col =   settings['spin_id_col']
            ds.relax_gui.free_file_format.mol_name_col =  settings['mol_name_col']
            ds.relax_gui.free_file_format.res_num_col =   settings['res_num_col']
            ds.relax_gui.free_file_format.res_name_col =  settings['res_name_col']
            ds.relax_gui.free_file_format.spin_num_col =  settings['spin_num_col']
            ds.relax_gui.free_file_format.spin_name_col = settings['spin_name_col']
            if self.data_cols:
                ds.relax_gui.free_file_format.data_col = settings['data_col']
                ds.relax_gui.free_file_format.error_col = settings['error_col']
            ds.relax_gui.free_file_format.sep = settings['sep']


    def set_vals(self):
        """Set the free file format widget contents to the values from the relax data store."""

        # The default GUI element.
        if self.element_type == 'default':
            # The column numbers.
            self.spin_id_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_id_col))
            self.mol_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.mol_name_col))
            self.res_num_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.res_num_col))
            self.res_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.res_name_col))
            self.spin_num_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_num_col))
            self.spin_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_name_col))
            if hasattr(self, 'data_col'):
                self.data_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.data_col))
            if hasattr(self, 'error_col'):
                self.error_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.error_col))

            # The column separator.
            if not ds.relax_gui.free_file_format.sep:
                self.sep.SetValue(str_to_gui("white space"))
            else:
                self.sep.SetValue(str_to_gui(ds.relax_gui.free_file_format.sep))

        # The mini GUI element.
        elif self.element_type == 'mini':
            # The string.
            if self.data_cols:
                string = self.to_string(spin_id_col=ds.relax_gui.free_file_format.spin_id_col, mol_name_col=ds.relax_gui.free_file_format.mol_name_col, res_num_col=ds.relax_gui.free_file_format.res_num_col, res_name_col=ds.relax_gui.free_file_format.res_name_col, spin_num_col=ds.relax_gui.free_file_format.spin_num_col, spin_name_col=ds.relax_gui.free_file_format.spin_name_col, data_col=ds.relax_gui.free_file_format.data_col, error_col=ds.relax_gui.free_file_format.error_col, sep=ds.relax_gui.free_file_format.sep)
            else:
                string = self.to_string(spin_id_col=ds.relax_gui.free_file_format.spin_id_col, mol_name_col=ds.relax_gui.free_file_format.mol_name_col, res_num_col=ds.relax_gui.free_file_format.res_num_col, res_name_col=ds.relax_gui.free_file_format.res_name_col, spin_num_col=ds.relax_gui.free_file_format.spin_num_col, spin_name_col=ds.relax_gui.free_file_format.spin_name_col, sep=ds.relax_gui.free_file_format.sep)
            self.field.SetValue(str_to_gui(string))


    def to_string(self, spin_id_col=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None):
        """Convert the free file format variables to string format.

        @keyword spin_id_col:   The column containing the spin ID strings (used by the generic intensity file format).  If supplied, the mol_name_col, res_name_col, res_num_col, spin_name_col, and spin_num_col arguments must be none.
        @type spin_id_col:      int or None
        @keyword mol_name_col:  The column containing the molecule name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
        @type mol_name_col:     int or None
        @keyword res_name_col:  The column containing the residue name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
        @type res_name_col:     int or None
        @keyword res_num_col:   The column containing the residue number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
        @type res_num_col:      int or None
        @keyword spin_name_col: The column containing the spin name information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
        @type spin_name_col:    int or None
        @keyword spin_num_col:  The column containing the spin number information (used by the generic intensity file format).  If supplied, spin_id_col must be None.
        @type spin_num_col:     int or None
        @keyword sep:           The column separator which, if None, defaults to whitespace.
        @type sep:              str or None
        @return:                The string representation of the free file format settings.
        @rtype:                 str
        """

        # The string.
        string = ''
        string += repr(spin_id_col)
        string += ', ' + repr(mol_name_col)
        string += ', ' + repr(res_num_col)
        string += ', ' + repr(res_name_col)
        string += ', ' + repr(spin_num_col)
        string += ', ' + repr(spin_name_col)
        if self.data_cols:
            string += ', ' + repr(data_col)
            string += ', ' + repr(error_col)
        if not sep:
            string += ', ' + repr("white space")
        else:
            string += ', ' + repr(sep)

        # Return the string.
        return string



class Free_file_format_window(wx.Dialog, Wiz_page):
    """The free file format setting window."""

    # The window size.
    SIZE = (500, 550)

    # A border.
    BORDER = 10

    # Sizes.
    SIZE_BUTTON = (100, 33)

    def __init__(self, parent=None):
        """Set up the window."""

        # Execute the base __init__() method.
        wx.Dialog.__init__(self, parent, id=-1, title="Free file format", style=wx.DEFAULT_FRAME_STYLE)

        # The sizes.
        self._main_size = self.SIZE[0] - 2*self.BORDER
        self._div_left = self._main_size / 2

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # The main sizer.
        self.main_sizer = self.build_frame()

        # The heading.
        text = wx.StaticText(self, -1, "Settings for the free file format")
        text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.main_sizer.Add(text, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer()

        # The relax logo.
        bmp = wx.StaticBitmap(self, -1, bitmap_setup(IMAGE_PATH+'relax.gif'))
        self.main_sizer.Add(bmp, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.main_sizer.AddStretchSpacer()

        # The centre section.
        self.add_centre(self.main_sizer)

        # The bottom buttons.
        self.add_buttons(self.main_sizer)

        # Set the window size.
        self.SetSize(self.SIZE)
        self.SetMinSize(self.SIZE)

        # Centre the window.
        self.Center()


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_CENTER|wx.ALL, 0)

        # The save button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Save")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.document-save', "22x22"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Save the free file format settings within the relax data store.")
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.save, button)

        # Spacer.
        button_sizer.AddSpacer(20)

        # The reset button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Reset")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.edit-delete', "22x22"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Reset the free file format settings to the original values.")
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.reset, button)

        # Spacer.
        button_sizer.AddSpacer(20)

        # The cancel button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "  Cancel")
        button.SetBitmapLabel(wx.Bitmap(fetch_icon('oxygen.actions.dialog-cancel', "22x22"), wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetMinSize(self.SIZE_BUTTON)
        button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, self.cancel, button)


    def add_centre(self, sizer):
        """Add the centre of the free file format settings window.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # The widget.
        self._element = Free_file_format(parent=self, sizer=sizer, data_cols=True, save=False, reset=False)

        # Spacing.
        self.main_sizer.AddStretchSpacer()


    def build_frame(self):
        """Create the main part of the frame, returning the central sizer."""

        # The sizers.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        central_sizer = wx.BoxSizer(wx.VERTICAL)

        # Left and right borders.
        sizer1.AddSpacer(self.BORDER)
        sizer1.Add(sizer2, 1, wx.EXPAND|wx.ALL, 0)
        sizer1.AddSpacer(self.BORDER)

        # Top and bottom borders.
        sizer2.AddSpacer(self.BORDER)
        sizer2.Add(central_sizer, 1, wx.EXPAND|wx.ALL, 0)
        sizer2.AddSpacer(self.BORDER)

        # Set the sizer for the frame.
        self.SetSizer(sizer1)

        # Return the central sizer.
        return central_sizer


    def cancel(self, event):
        """Close the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Destroy the window.
        self.Destroy()


    def reset(self, event):
        """Reset the free file format settings.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the base class method.
        self._element.reset(event)


    def save(self, event):
        """Save the free file format widget contents into the relax data store.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the base class method.
        self._element.save(event)

        # Destroy the window.
        self.Destroy()
