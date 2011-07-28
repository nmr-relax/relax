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
"""Base class module for the wizard GUI elements."""

# Python module imports.
import wx
from wx.lib import buttons, scrolledpanel

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import id_string_doc
from relax_errors import RelaxImplementError
from status import Status; status = Status()

# relax GUI module imports.
from gui.controller import Redirect_text
from gui.filedialog import openfile
from gui.icons import relax_icons
from gui.misc import add_border, bool_to_gui, gui_to_int, int_to_gui, protected_exec, str_to_gui
from gui import paths


class File_selector:
    """Class for handling file selection dialogs and updating the respective fields."""

    def __init__(self, field, title='File selection', default="all files (*.*)|*"):
        """Setup the class and store the field.

        @param field:       The field to update with the file selection.
        @type field:        wx.TextCtrl instance
        @keyword title:     The text title to put at the top of the dialog window.
        @type title:        str
        @keyword default:   The default file type.
        @type default:      str
        """

        # Store the args.
        self.field = field
        self.title = title
        self.default = default


    def select(self, event):
        """The file selector GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the file selection dialog.
        file = openfile(msg=self.title, default=self.default)

        # Check the file.
        if not file:
            return

        # Update the field.
        self.field.SetValue(file)

        # Scroll the text to the end.
        self.field.SetInsertionPoint(len(file))



class Wiz_page(wx.Panel):
    """The wizard pages to be placed inside the wizard.

    To inherit from this class, you must minimally supply the add_contents() method.  This method should build the specific GUI elements.  The following methods are also designed to be overwritten:

        - add_artwork(), this builds the left hand artwork section of the page.
        - add_contents(), this builds the right hand section of the page.
        - on_display(), this is executed when the page is displayed.
        - on_display_post(), this is executed when the page is displayed, directly after the on_display method.
        - on_execute(), this is executed when the wizard is terminated or the apply button is hit.
        - on_next(), this is executed when moving to the next wizard page.

    The following methods can be used by add_contents() to create standard GUI elements:

        - chooser()
        - combo_box()
        - file_selection()
        - free_file_format()
        - input_field()
        - text()

    These are described in full detail in their docstrings.
    """

    # Some class variables.
    art_spacing = 20
    divider = None
    height_desc = 220
    height_element = 27
    image_path = paths.IMAGE_PATH + "relax.gif"
    main_text = ''
    title = ''

    def __init__(self, parent):
        """Set up the window.

        @param parent:  The parent GUI element.
        @type parent:   wx.object instance
        """

        # Store the args.
        self.parent = parent

        # Execute the base class method.
        wx.Panel.__init__(self, parent, id=-1)

        # Initilise some variables.
        self.exec_status = False

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(box_main)

        # Add the artwork.
        self.add_artwork(box_main)

        # The size of the image.
        image_x, image_y = self.image.GetSize()

        # Calculate the size of the main section, and the subdivisions.
        self._main_size = parent._size_x - image_x - self.art_spacing - 2*parent._border
        if self.divider:
            self._div_left = self.divider
            self._div_right = self._main_size - self.divider
        else:
            self._div_left = self._div_right = self._main_size / 2

        # Add the main sizer.
        main_sizer = self._build_main_section(box_main)

        # Add the title.
        self._add_title(main_sizer)

        # Add the description.
        self.add_desc(main_sizer, max_y=self.height_desc)

        # Add the specific GUI elements (bounded by spacers).
        main_sizer.AddStretchSpacer()
        self.add_contents(main_sizer)


    def _add_title(self, sizer):
        """Add the title to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Spacing.
        sizer.AddSpacer(10)

        # The text.
        title = wx.StaticText(self, -1, self.title)

        # Font.
        title.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

        # Add the title.
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 0)

        # Spacing.
        sizer.AddSpacer(10)


    def _apply(self, event):
        """Apply the operation.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute.
        self.exec_status = protected_exec(self.on_execute)

        # Execution failure.
        if not self.exec_status:
            return

        # Finished.
        self.on_completion()

        # Execute the on_apply() method.
        self.on_apply()


    def _build_main_section(self, sizer):
        """Add the main part of the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        @return:        The sizer object for the main part of the dialog.
        @rtype:         wx.Sizer instance
        """

        # Use a grid sizer for packing the elements.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer.
        sizer.Add(main_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Return the sizer.
        return main_sizer


    def _free_file_format_save(self, event):
        """Save the free file format widget contents into the relax data store.

        @param event:   The wx event.
        @type event:    wx event
        """

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
        if hasattr(self, 'err_col'):
            ds.relax_gui.free_file_format.err_col = gui_to_int(self.err_col.GetValue())

        # The column separator.
        ds.relax_gui.free_file_format.sep = str(self.sep.GetValue())
        if ds.relax_gui.free_file_format.sep == 'white space':
            ds.relax_gui.free_file_format.sep = None


    def add_artwork(self, sizer):
        """Add the artwork to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add the graphics.
        if self.image_path:
            self.image = wx.StaticBitmap(self, -1, wx.Bitmap(self.image_path, wx.BITMAP_TYPE_ANY))
            sizer.Add(self.image, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # A spacer.
        sizer.AddSpacer(self.art_spacing)


    def add_contents(self, sizer):
        """Add the specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # This must be supplied.
        raise RelaxImplementError


    def add_desc(self, sizer, max_y=220):
        """Add the description to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        @keyword max_y: The maximum height, in number of pixels, for the description.
        @type max_y:    int
        """

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)

        # Create a scrolled panel.
        panel = scrolledpanel.ScrolledPanel(self, -1, name="desc")

        # A sizer for the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # The text.
        text = wx.StaticText(panel, -1, self.main_text, style=wx.TE_MULTILINE)

        # Font.
        #text.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

        # Wrap the text.
        text.Wrap(self._main_size - 20)

        # The text size.
        x, y = text.GetSizeTuple()

        # Scrolling needed.
        if y > max_y-10:
            # Set the panel size.
            panel.SetInitialSize((self._main_size, max_y))

        # No scrolling.
        else:
            # Rewrap the text.
            text.Wrap(self._main_size)

            # Set the panel size.
            panel.SetInitialSize(text.GetSize())

        # Add the text.
        panel_sizer.Add(text, 0, wx.ALIGN_LEFT, 0)

        # Set up and add the panel to the sizer.
        panel.SetSizer(panel_sizer)
        panel.SetAutoLayout(1)
        panel.SetupScrolling(scroll_x=False, scroll_y=True)
        sizer.Add(panel, 0, wx.ALL|wx.EXPAND)

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)


    def boolean_selector(self, sizer, desc, tooltip=None, divider=None, padding=0, spacer=None, default=True):
        """Build the boolean selector widget for selecting between True and False.

        @param sizer:       The sizer to put the combo box widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @keyword default:   The default boolean value.
        @type default:      bool
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The combo box element.
        style = wx.CB_DROPDOWN | wx.CB_READONLY
        combo = wx.ComboBox(self, -1, value=bool_to_gui(default), style=style, choices=['True', 'False'])
        combo.SetMinSize((50, self.height_element))
        sub_sizer.Add(combo, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer.
        sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if spacer == None:
            sizer.AddStretchSpacer()
        else:
            sizer.AddSpacer(spacer)

        # Tooltip.
        if tooltip:
            text.SetToolTipString(tooltip)
            combo.SetToolTipString(tooltip)

        # Return the combo box element.
        return combo


    def chooser(self, sizer, desc, func, choices):
        """Build the choice element.

        @param sizer:   The sizer to put the input field into.
        @type sizer:    wx.Sizer instance
        @param desc:    The text description.
        @type desc:     str
        @param func:    The function to bind the event to
        @type func:     func
        @param choices: The list of choices.
        @type choices:  list of str
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 1, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sub_sizer.AddSpacer(10)

        # The choice element.
        type_choice = wx.Choice(self, -1, style=wx.ALIGN_LEFT, choices=choices)
        sub_sizer.Add(type_choice, 1, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        self.Bind(wx.EVT_CHOICE, func, type_choice)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(sub_sizer)
        sizer.AddStretchSpacer()


    def combo_box(self, sizer, desc, choices=[], evt_fn=None, tooltip=None, divider=None, padding=0, spacer=None, read_only=True):
        """Build the combo box widget for list selections.

        @param sizer:       The sizer to put the combo box widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @param choices:     The list of choices.
        @type choices:      list of str
        @param evt_fn:      The event handling function.
        @type evt_fn:       func
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @keyword read_only: A flag which if True means that text cannot be typed into the combo box widget.
        @type read_only:    bool
        @return:            The combo box object.
        @rtype:             wx.ComboBox instance
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The combo box element.
        style = wx.CB_DROPDOWN
        if read_only:
            style = style | wx.CB_READONLY
        combo = wx.ComboBox(self, -1, value='', style=style, choices=choices)
        combo.SetMinSize((50, self.height_element))
        sub_sizer.Add(combo, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer.
        sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if spacer == None:
            sizer.AddStretchSpacer()
        else:
            sizer.AddSpacer(spacer)

        # Bind events.
        if evt_fn:
            self.Bind(wx.EVT_COMBOBOX, evt_fn, combo)

        # Tooltip.
        if tooltip:
            text.SetToolTipString(tooltip)
            combo.SetToolTipString(tooltip)

        # Return the combo box element.
        return combo


    def file_selection(self, sizer, desc, title='File selection', default="all files (*.*)|*", tooltip=None, divider=None, padding=0, spacer=None):
        """Build the file selection element.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword title:     The text title to put at the top of the dialog window.
        @type title:        str
        @keyword default:   The default file type.
        @type default:      str
        @keyword tooltip:   The tooltip which appears on hovering over all the GUI elements.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @return:            The file selection GUI element.
        @rtype:             wx.TextCtrl
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        field = wx.TextCtrl(self, -1, '')
        field.SetMinSize((-1, self.height_element))
        sub_sizer.Add(field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # The file selection object.
        obj = File_selector(field, title=title, default=default)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The file selection button.
        button = wx.BitmapButton(self, -1, wx.Bitmap(paths.icon_16x16.open, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((self.height_element, self.height_element))
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        self.Bind(wx.EVT_BUTTON, obj.select, button)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if spacer == None:
            sizer.AddStretchSpacer()
        else:
            sizer.AddSpacer(spacer)

        # Tooltip.
        if tooltip:
            text.SetToolTipString(tooltip)
            field.SetToolTipString(tooltip)
            button.SetToolTipString(tooltip)
        else:
            button.SetToolTipString("Select the file.")

        # Return the field element.
        return field


    def free_file_format(self, sizer, padding=10, spacer=3, data_cols=False, save=True):
        """Build the free format file settings widget.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @keyword padding:   The size of the padding between the wx.StaticBoxSizer border and the internal elements, in pixels.
        @type padding:      int
        @keyword spacer:    The horizontal spacing between the elements, in pixels.
        @type spacer:       int
        @keyword data_cols: A flag which if True causes the data and error column elements to be displayed.
        @type data_cols:    bool
        @keyword save:      A flag which if True will cause the save button to be displayed.
        @type save:         bool
        """

        # A static box to hold all the widgets.
        box = wx.StaticBox(self, -1, "Free format file settings")

        # Init.
        sub_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sub_sizer.AddSpacer(padding)
        divider = self._div_left - 15

        # The columns.
        self.spin_id_col = self.input_field(sub_sizer, "Spin ID column:", divider=divider, padding=padding, spacer=spacer)
        self.mol_name_col = self.input_field(sub_sizer, "Molecule name column:", divider=divider, padding=padding, spacer=spacer)
        self.res_num_col = self.input_field(sub_sizer, "Residue number column:", divider=divider, padding=padding, spacer=spacer)
        self.res_name_col = self.input_field(sub_sizer, "Residue name column:", divider=divider, padding=padding, spacer=spacer)
        self.spin_num_col = self.input_field(sub_sizer, "Spin number column:", divider=divider, padding=padding, spacer=spacer)
        self.spin_name_col = self.input_field(sub_sizer, "Spin name column:", divider=divider, padding=padding, spacer=spacer)
        if data_cols:
            self.data_col = self.input_field(sub_sizer, "Data column:", divider=divider, padding=padding, spacer=spacer)
            self.err_col = self.input_field(sub_sizer, "Error column:", divider=divider, padding=padding, spacer=spacer)

        # Set the values.
        self.spin_id_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_id_col))
        self.mol_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.mol_name_col))
        self.res_num_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.res_num_col))
        self.res_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.res_name_col))
        self.spin_num_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_num_col))
        self.spin_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_name_col))
        if data_cols:
            self.data_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.data_col))
            self.err_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.err_col))

        # The column separator.
        self.sep = self.combo_box(sub_sizer, "Column separator:", ["white space", ",", ";", ":", ""], divider=divider, padding=padding, spacer=spacer, read_only=False)
        if not ds.relax_gui.free_file_format.sep:
            self.sep.SetValue("white space")
        else:
            self.sep.SetValue(str_to_gui(ds.relax_gui.free_file_format.sep))

        # Add a save button.
        if save:
            # A sizer.
            button_sizer = wx.BoxSizer(wx.HORIZONTAL)

            # Build the button.
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, "  Save")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.save, wx.BITMAP_TYPE_ANY))
            button.SetToolTipString("Save the free file format settings within the relax data store")

            # Add the button.
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

            # Right padding.
            button_sizer.AddSpacer(padding)

            # Bind the click event.
            self.Bind(wx.EVT_BUTTON, self._free_file_format_save, button)

            # Add the button sizer to the widget (with spacing).
            sub_sizer.AddSpacer(padding)
            sub_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT|wx.ALL, 0)

        # Set the size of the widget.
        sub_sizer.AddSpacer(padding)
        x, y = box.GetSize()
        box.SetMinSize((self._main_size, y))

        # The border of the widget.
        border = wx.BoxSizer()

        # Place the box sizer inside the border.
        border.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(border, 0, wx.EXPAND)
        sizer.AddStretchSpacer()


    def input_field(self, sizer, desc, tooltip=None, divider=None, padding=0, spacer=None):
        """Build the input field widget.

        @param sizer:       The sizer to put the input field widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @return:            The input field object.
        @rtype:             wx.TextCtrl instance
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        field = wx.TextCtrl(self, -1, '')
        field.SetMinSize((50, self.height_element))
        sub_sizer.Add(field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer.
        sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if spacer == None:
            sizer.AddStretchSpacer()
        else:
            sizer.AddSpacer(spacer)

        # Tooltip.
        if tooltip:
            text.SetToolTipString(tooltip)
            field.SetToolTipString(tooltip)

        # Return the object.
        return field


    def on_apply(self):
        """To be over-ridden if an action is to be performed on hitting the apply button.

        This method will be called when clicking on the apply button.  The default behaviour is to call the on_display() and on_display_post() method.
        """

        # Call the on_display method by default.
        self.on_display()
        self.on_display_post()


    def on_completion(self):
        """To be over-ridden if an action is to be performed just after executing self.on_execute().

        This method is called just after self.on_execute() has been called
        """


    def on_display(self):
        """To be over-ridden if an action is to be performed prior to displaying the page.

        This method will be called by the wizard class method _display_page() just after hiding all other pages but prior to displaying this page.
        """


    def on_display_post(self):
        """To be over-ridden if an action is to be performed after the execution of the on_display() method.

        This method will be called by the wizard class method _display_page() just after hiding all other pages but prior to displaying this page.
        """


    def on_execute(self):
        """To be over-ridden if an action is to be performed just before exiting the page.

        This method is called when terminating the wizard or hitting the apply button. 
        """


    def on_next(self):
        """To be over-ridden if an action is to be performed just before moving to the next page.

        This method is called when moving to the next page of the wizard.
        """


    def spin_id_element(self, sizer, desc="The spin ID string:", choices=['@N', '@C'], default=None, divider=None, padding=0, spacer=None):
        """Build a special the input field widget.

        @param sizer:       The sizer to put the input field widget into.
        @type sizer:        wx.Sizer instance
        @keyword desc:      The text description.
        @type desc:         str
        @keyword choices:   The list of choices to present to the user.
        @type choices:      list of str
        @keyword default:   The default value.
        @type default:      str or None
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @return:            The input field object.
        @rtype:             wx.TextCtrl instance
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        field = wx.ComboBox(self, -1, '', choices=choices)
        field.SetMinSize((50, self.height_element))
        sub_sizer.Add(field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Set the default.
        field.SetValue(str_to_gui(default))

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer.
        sizer.Add(sub_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Spacing below the widget.
        if spacer == None:
            sizer.AddStretchSpacer()
        else:
            sizer.AddSpacer(spacer)

        # Tooltip (the ID string documentation, with starting and ending newlines removed).
        text.SetToolTipString(id_string_doc[1][1:-1])
        field.SetToolTipString(id_string_doc[1][1:-1])

        # Return the object.
        return field


    def text(self, sizer, desc, default='', divider=None, padding=0, spacer=None):
        """Build the input field.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword default:   The default text.
        @type default:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @return:            The input field object.
        @rtype:             wx.TextCtrl instance
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The non-editable text.
        text = wx.TextCtrl(self, -1, default, style=wx.ALIGN_LEFT)
        text.SetEditable(False)
        colour = self.GetBackgroundColour()
        text.SetOwnBackgroundColour(colour)
        text.SetMinSize((self._div_right, self.height_element))
        sub_sizer.Add(text, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Right padding.
        sub_sizer.AddSpacer(padding)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(sub_sizer)

        # Spacing below the widget.
        if spacer == None:
            sizer.AddStretchSpacer()
        else:
            sizer.AddSpacer(spacer)

        # Return the object.
        return text



class Wiz_window(wx.Dialog):
    """The wizard."""

    # Some class variables.
    _size_button = (100, 33)

    def __init__(self, size_x=400, size_y=400, title='', border=10, style=wx.DEFAULT_DIALOG_STYLE):
        """Set up the window.

        @keyword style:     The dialog style.
        @type style:        wx style
        """

        # Store the args.
        self._size_x = size_x
        self._size_y = size_y
        self._border = border

        # Execute the base class method.
        wx.Dialog.__init__(self, None, id=-1, title=title, style=style)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # The sizer for the dialog.
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Build the central sizer, with borders.
        self._main_sizer = add_border(sizer, border=border, packing=wx.VERTICAL)

        # Set the default size of the dialog.
        self.SetSize((size_x, size_y))

        # Centre the dialog.
        self.Centre()

        # Initialise the wizard status.
        self._status = True

        # Initialise the page storage.
        self._current_page = 0
        self._num_pages = 0
        self._pages = []
        self._page_sizers = []
        self._button_sizers = []
        self._button_apply_flag = []
        self._button_skip_flag = []
        self._buttons = []
        self._button_ids = []
        self._exec_on_next = []
        self._exec_count = []
        self._proceed_on_error = []
        self._seq_fn_list = []
        self._seq_next = []
        self._seq_prev = []
        self._skip_flag = []

        # A max of 10 pages should be plenty enough (any more and the developer should be shot!).
        for i in range(10):
            # Append some Nones.
            self._pages.append(None)

            # Initialise all box sizers for the wizard pages.
            self._page_sizers.append(wx.BoxSizer(wx.VERTICAL))

            # Initialise all box sizers for the buttons.
            self._button_sizers.append(wx.BoxSizer(wx.HORIZONTAL))

            # Set all button flags.
            self._button_apply_flag.append(True)
            self._button_skip_flag.append(False)

            # Initialise the button storage.
            self._buttons.append({'back': None,
                                  'apply': None,
                                  'next': None,
                                  'ok': None,
                                  'finish': None,
                                  'cancel': None})

            # Initialise a set of unique button IDs.
            self._button_ids.append({'back': wx.NewId(),
                                     'apply': wx.NewId(),
                                     'next': wx.NewId(),
                                     'ok': wx.NewId(),
                                     'finish': wx.NewId(),
                                     'cancel': wx.NewId()})

            # Execute on next by default.
            self._exec_on_next.append(True)

            # Execution count.
            self._exec_count.append(0)

            # Proceed to next page on errors by default.
            self._proceed_on_error.append(True)

            # Page sequence initialisation.
            self._seq_fn_list.append(self._next_fn)
            self._seq_next.append(None)
            self._seq_prev.append(None)

            # Page skipping.
            self._skip_flag.append(False)


    def _build_buttons(self):
        """Construct the buttons for all pages of the wizard."""

        # Loop over each page.
        for i in range(self._num_pages):
            # The back button (only for multi-pages, after the first).
            if self._num_pages > 1 and i > 0:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, " Back")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.go_previous_view, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Return to the previous page")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._go_back, button)
                self._buttons[i]['back'] = button

                # Spacer.
                self._button_sizers[i].AddSpacer(5)

            # The apply button.
            if self._button_apply_flag[i]:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, " Apply")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.apply, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Apply the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._pages[i]._apply, button)
                self._buttons[i]['apply'] = button

                # Spacer.
                self._button_sizers[i].AddSpacer(5)

            # The skip button.
            if self._button_skip_flag[i]:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, " Skip")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.skip, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Skip the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._skip, button)
                self._buttons[i]['skip'] = button

                # Spacer.
                self._button_sizers[i].AddSpacer(5)

            # The next button (only for multi-pages, excluding the last).
            if self._num_pages > 1 and i < self._num_pages - 1:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, " Next")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.go_next_view, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Move to the next page")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._go_next, button)
                self._buttons[i]['next'] = button

            # The OK button (only for single pages).
            if self._num_pages == 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, " OK")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.ok, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Accept the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._ok, button)
                self._buttons[i]['ok'] = button

            # The finish button (only for the last page with multi-pages).
            if self._num_pages > 1 and i == self._num_pages - 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, " Finish")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.ok, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Accept the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._ok, button)
                self._buttons[i]['finish'] = button

            # Spacer.
            self._button_sizers[i].AddSpacer(15)

            # The cancel button.
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, " Cancel")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.cancel, wx.BITMAP_TYPE_ANY))
            button.SetToolTipString("Abort the operation")
            button.SetMinSize(self._size_button)
            self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self._cancel, button)
            self._buttons[i]['cancel'] = button


    def _cancel(self, event):
        """Cancel the operation.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Change the status.
        self._status = False

        # Close the window.
        self.Close()


    def _display_page(self, i):
        """Display the given page.

        @param i:   The index of the page to display.
        @type i:    int
        """

        # Hide all of the original contents.
        for j in range(self._num_pages):
            self._main_sizer.Hide(self._page_sizers[j])

        # Execute the page's on_display() method.
        self._pages[i].on_display()
        self._pages[i].on_display_post()

        # Show the desired page.
        if status.show_gui:
            self._main_sizer.Show(self._page_sizers[i])

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()


    def _go_back(self, event):
        """Return to the previous page.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Work back in the sequence.
        self._current_page = self._seq_prev[self._current_page]

        # Display the previous page.
        self._display_page(self._current_page)


    def _go_next(self, event):
        """Move to the next page.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Operations for non-skipped pages.
        if not self._skip_flag[self._current_page]:
            # Execute the page's on_next() method.
            self._pages[self._current_page].on_next()

            # Execute the page's on_execute() method (via the _apply() method).
            if self._exec_on_next[self._current_page]:
                self._pages[self._current_page]._apply(event)

                # Check for execution errors.
                if not self._pages[self._current_page].exec_status:
                    # Do not proceed.
                    if not self._proceed_on_error[self._current_page]:
                        return

                # Increment the execution counter.
                self._exec_count[self._current_page] += 1

        # Determine the next page.
        next_page = self._seq_fn_list[self._current_page]()

        # No next page, so terminate.
        if self._pages[next_page] == None:
            self._ok(None)
            return

        # Update the sequence lists.
        self._seq_next[self._current_page] = next_page
        self._seq_prev[next_page] = self._current_page

        # Change the current page.
        self._current_page = next_page

        # Display the next page.
        self._display_page(self._current_page)


    def _next_fn(self):
        """Standard function for setting the next page to the one directly next in the sequence.

        @return:    The index of the next page, which is the current page index plus one.
        @rtype:     int
        """

        # Return the next page.
        return self._current_page + 1

        
    def _ok(self, event):
        """Accept the operation.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Loop over the pages in the sequence and execute their _apply() methods, if not already done and not skipped.
        for i in self._seq_loop():
            if not self._exec_count[i] and not self._skip_flag[i]:
                # Execute the _apply method.
                self._pages[i]._apply(event)

                # Increment the execution counter.
                self._exec_count[i] += 1

        # Then close the dialog.
        self.Close()


    def _seq_loop(self):
        """Loop over the sequence in the forwards direction."""

        # Initialise.
        current = 0

        # First yield the initial element (always zero!).
        yield current

        # Loop over the sequence.
        while 1:
            # Update.
            next = self._seq_next[current]
            current = next

            # End of the sequence.
            if next == None:
                break

            # Yield the next index.
            yield next


    def _skip(self, event):
        """Skip the page.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the skip flag.
        self._skip_flag[self._current_page] = True

        # Go to the next page.
        self._go_next(None)


    def add_page(self, panel, apply_button=True, skip_button=False, exec_on_next=True, proceed_on_error=True):
        """Add a new page to the wizard.

        @param panel:               The page to add to the wizard.
        @type panel:                wx.Panel instance
        @keyword apply_button:      A flag which if true will show the apply button for that page.
        @type apply_button:         bool
        @keyword skip_button:       A flag which if true will show the skip button for that page.
        @type skip_button:          bool
        @keyword exec_on_next:      A flag which if true will run the on_execute() method when clicking on the next button.
        @type exec_on_next:         bool
        @keyword proceed_on_error:  A flag which if True will proceed to the next page (or quit if there are no more pages) despite the occurrence of an error in execution.  If False, the page will remain open.
        @type proceed_on_error:     bool
        @return:                    The index of the page in the wizard.
        @rtype:                     int
        """

        # Store the page.
        index = self._num_pages
        self._num_pages += 1
        self._pages[index] = panel

        # Store a new sizer for the page and its buttons.
        self._main_sizer.Add(self._page_sizers[index], 1, wx.ALL|wx.EXPAND, 0)

        # Add the sizer for the top half.
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        self._page_sizers[index].Add(top_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add the page to the top sizer.
        top_sizer.Add(panel, 1, wx.ALL|wx.EXPAND, 0)

        # Add the sizer for the wizard buttons.
        self._page_sizers[index].Add(self._button_sizers[index], 0, wx.ALIGN_RIGHT|wx.ALL, 0)

        # Store the flags.
        self._button_apply_flag[index] = apply_button
        self._button_skip_flag[index] = skip_button
        self._exec_on_next[index] = exec_on_next
        self._proceed_on_error[index] = proceed_on_error

        # Store the index of the page.
        panel.page_index = self._num_pages - 1

        # Return the index of the page.
        return panel.page_index


    def block_next(self, block=True):
        """Prevent moving forwards (or unblock).

        @keyword block: A flag which if True will block forwards movement and if False will unblock.
        @type block:    bool
        """

        # The buttons to disable.
        buttons = ['next', 'ok', 'finish']

        # Disable or enable the buttons.
        for i in range(len(buttons)):
            # The button.
            button = self._buttons[self._current_page][buttons[i]]
            if button == None:
                continue

            # Block.
            if block:
                button.Disable()

            # Unblock.
            else:
                button.Enable()


    def get_page(self, index):
        """Get a page from the wizard.

        @param index:   The index of the page.
        @type index:    int
        @return:        The page object.
        @rtype:         Wiz_page instance.
        """

        # Return the page.
        return self._pages[index]


    def run(self, modal=False):
        """Execute the wizard.

        @keyword modal: A flag which if True will cause the wizard to be run as a modal dialog.
        @type modal:    bool
        @return:        The status from the modal operation, i.e. True if the wizard is run, False if cancelled or other error occur.  For modeless operation, this returns nothing.
        @rtype:         bool or None
        """

        # Build the buttons for the entire wizard.
        self._build_buttons()

        # Display the first page.
        self._display_page(0)

        # No GUI.
        if not status.show_gui:
            return

        # Modal operation.
        if modal:
            # Show the wizard (it should be closed by the _cancel() or _ok() methods).
            self.ShowModal()

            # Return the status.
            return self._status

        # Modeless operation.
        else:
            # Show the wizard.
            self.Show()


    def set_seq_next_fn(self, index, fn):
        """A user specified function for non-linear page changing.

        @param index:   The index of the page the function should be associated with.
        @type index:    int
        @param fn:      The function for determining the page after the current.  This function should return the index of the next page.
        @type fn:       func or method.
        """

        # Store the function.
        self._seq_fn_list[index] = fn
