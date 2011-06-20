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
from wx.lib import buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import AllRelaxErrors, RelaxImplementError

# relax GUI module imports.
from gui.controller import Redirect_text
from gui.filedialog import openfile
from gui.message import error_message
from gui.misc import add_border, gui_to_int, int_to_gui, str_to_gui
from gui import paths


class File_selector:
    """Class for handling file selection dialogs and updating the respective fields."""

    def __init__(self, field, title='File selection', default="all files (*.*)|*"):
        """Setup the class and store the field.

        @param field:   The field to update with the file selection.
        @type field:    wx.TextCtrl instance
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



class Wiz_panel(wx.Panel):
    """The panel base class to be placed inside the wizard-like window.

    To inherit from this class, you must supply the add_contents() and execute() methods.  The add_contents() method should build the specific GUI elements, and the execute() method is called when clicking on the apply or ok buttons.
    """

    # Some class variables.
    art_spacing = 20
    divider = None
    image_path = None
    input_size = 27
    main_text = ''
    title = ''

    def __init__(self, parent):
        """Set up the window.

        @param parent:  The parent GUI element.
        @type parent:   wx.object instance
        """

        # Execute the base class method.
        wx.Panel.__init__(self, parent, id=-1)

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(box_main)

        # Add the artwork.
        self.add_artwork(box_main)

        # The size of the image.
        image_x, image_y = self.image.GetSize()

        # Calculate the size of the main section, and the subdivisions.
        self.main_size = parent.size_x - image_x - self.art_spacing - 2*parent.border
        if self.divider:
            self.div_left = self.divider
            self.div_right = self.main_size - self.divider
        else:
            self.div_left = self.div_right = self.main_size / 2

        # Add the main sizer.
        main_sizer = self.build_main_section(box_main)

        # Add the title.
        self.add_title(main_sizer)

        # Add the description.
        self.add_desc(main_sizer)

        # Add the specific GUI elements (bounded by spacers).
        main_sizer.AddStretchSpacer()
        self.add_contents(main_sizer)
        main_sizer.AddStretchSpacer()
        main_sizer.AddStretchSpacer()

        # Bind some events.
        self.Bind(wx.EVT_SHOW, self.update)


    def add_artwork(self, sizer):
        """Add the artwork to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Add the graphics.
        if self.image_path:
            self.image = wx.StaticBitmap(self, -1, wx.Bitmap(self.image_path, wx.BITMAP_TYPE_ANY))

            # Add the relax logo.
            sizer.Add(self.image, 0, wx.TOP|wx.ALIGN_CENTER_HORIZONTAL, 0)

        # A spacer.
        sizer.AddSpacer(self.art_spacing)


    def add_desc(self, sizer):
        """Add the description to the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)

        # The text.
        text = wx.StaticText(self, -1, self.main_text, style=wx.TE_MULTILINE)

        # Font.
        #text.SetFont(wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.NORMAL))

        # Wrap the text.
        text.Wrap(self.main_size)

        # Add the text.
        sizer.Add(text, 0, wx.ALIGN_LEFT|wx.ALL, 0)

        # A line with spacing.
        sizer.AddSpacer(5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 0)
        sizer.AddSpacer(5)


    def add_title(self, sizer):
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


    def add_contents(self, sizer):
        """Add the specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        raise RelaxImplementError


    def apply(self, event):
        """Apply the operation.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute.
        try:
            self.execute()
        except AllRelaxErrors, instance:
            error_message(instance.text, instance.__class__.__name__)


    def build_central_section(self, sizer):
        """Add the centre part of the dialog.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        @return:        The sizer object for the centre part of the dialog.
        @rtype:         wx.Sizer instance
        """

        # Use a grid sizer for packing the elements.
        centre_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Pack the sizer into the frame.
        sizer.Add(centre_sizer, 1, wx.EXPAND|wx.ALL, 0)

        # Return the sizer.
        return centre_sizer


    def build_main_section(self, sizer):
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


    def cancel(self, event):
        """Cancel the operation.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close.
        self.Close()


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
        @keyword divider:   The optional position of the divider.  If None, the class variable div_left will be used.
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
            divider = self.div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The combo box element.
        style = wx.CB_DROPDOWN
        if read_only:
            style = style | wx.CB_READONLY
        combo = wx.ComboBox(self, -1, value='', style=style, choices=choices)
        combo.SetMinSize((50, 27))
        sub_sizer.Add(combo, 1, wx.ALIGN_CENTER_VERTICAL, 0)

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


    def execute(self):
        """Execute the operation (dummy method)."""

        raise RelaxImplementError


    def file_selection(self, sizer, desc, title='File selection', default="all files (*.*)|*"):
        """Build the file selection element.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword title:     The text title to put at the top of the dialog window.
        @type title:        str
        @keyword default:   The default file type.
        @type default:      str
        @return:            The file selection GUI element.
        @rtype:             wx.TextCtrl
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((self.div_left - x, 0))

        # The input field.
        field = wx.TextCtrl(self, -1, '')
        field.SetMinSize((self.div_right - 27, 27))
        sub_sizer.Add(field, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # The file selection object.
        obj = File_selector(field, title=title, default=default)

        # The file selection button.
        button = wx.BitmapButton(self, -1, wx.Bitmap(paths.icon_16x16.open, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Select the file")
        button.SetMinSize((27, 27))
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
        self.Bind(wx.EVT_BUTTON, obj.select, button)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(sub_sizer)
        sizer.AddStretchSpacer()

        # Return the field element.
        return field


    def free_file_format(self, sizer, data_cols=False, save=True):
        """Build the free format file settings widget.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @keyword data_cols: A flag which if True causes the data and error column elements to be displayed.
        @type data_cols:    bool
        @keyword save:      A flag which if True will cause the save button to be displayed.
        @type save:         bool
        """

        # A static box to hold all the widgets.
        box = wx.StaticBox(self, -1, "Free format file settings")

        # Init.
        sub_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        sub_sizer.AddSpacer(10)
        divider = self.div_left - 15
        padding = 10
        spacer = 3

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
            self.Bind(wx.EVT_BUTTON, self.free_file_format_save, button)

            # Add the button sizer to the widget (with spacing).
            sub_sizer.AddSpacer(10-spacer)
            sub_sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT|wx.ALL, 0)

        # Set the size of the widget.
        sub_sizer.AddSpacer(10)
        x, y = box.GetSize()
        box.SetMinSize((self.main_size, y))

        # The border of the widget.
        border = wx.BoxSizer()

        # Place the box sizer inside the border.
        border.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(border, 0, wx.EXPAND)
        sizer.AddStretchSpacer()


    def free_file_format_save(self, event):
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


    def input_field(self, sizer, desc, tooltip=None, divider=None, padding=0, spacer=None):
        """Build the input field widget.

        @param sizer:       The sizer to put the input field widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable div_left will be used.
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
            divider = self.div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        field = wx.TextCtrl(self, -1, '')
        field.SetMinSize((50, 27))
        sub_sizer.Add(field, 1, wx.ALIGN_CENTER_VERTICAL, 0)

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


    def ok(self, event):
        """Accept the operation.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the apply method.
        self.apply(event)

        # Then close.
        self.Close()


    def text(self, sizer, desc, default=''):
        """Build the input field.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword default:   The default text.
        @type default:      str
        @return:            The input field object.
        @rtype:             wx.TextCtrl instance
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((self.div_left - x, 0))

        # The non-editable text.
        text = wx.TextCtrl(self, -1, default, style=wx.ALIGN_LEFT)
        text.SetEditable(False)
        colour = self.GetBackgroundColour()
        text.SetOwnBackgroundColour(colour)
        text.SetMinSize((self.div_right, 27))
        sub_sizer.Add(text, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # Add to the main sizer (followed by stretchable spacing).
        sizer.Add(sub_sizer)
        sizer.AddStretchSpacer()

        # Return the object.
        return text


    def update(self, event):
        """Dummy method for updating the UI."""



class Wiz_window(wx.Dialog):
    """Wizard-like window GUI element base class.

    To inherit from this class, you must supply the add_contents() and execute() methods.  The add_contents() method should build the specific GUI elements, and the execute() method is called when clicking on the apply or ok buttons.
    """

    def __init__(self, size_x=None, size_y=None, title='', border=10, style=wx.DEFAULT_DIALOG_STYLE):
        """Set up the window.

        @keyword style:     The dialog style.
        @type style:        wx style
        """

        # Store the args.
        self.size_x = size_x
        self.size_y = size_y
        self.border = border

        # Execute the base class method.
        wx.Dialog.__init__(self, None, id=-1, title=title, style=style)

        # The sizer for the dialog.
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        # Build the central sizer, with borders.
        self.main_sizer = add_border(sizer, border=border, packing=wx.VERTICAL)

        # Set the default size of the dialog.
        self.SetSize((size_x, size_y))

        # Centre the dialog.
        self.Centre()

        # Initialise the page storage.
        self.pages = []
        self.page_sizers = []
        self.button_sizers = []
        self.button_flags = []
        self.button_apply = []


    def add_page(self, panel, apply_button=True):
        """Add a new page to the wizard.

        @param panel:           The page to add to the wizard.
        @type panel:            wx.Panel instance
        @keyword apply_button:  A flag which if true will show the apply button for that page.
        @type apply_button:     bool
        """

        # Store the page.
        self.pages.append(panel)

        # Store a new sizer for the page and its buttons.
        self.page_sizers.append(wx.BoxSizer(wx.VERTICAL))
        self.main_sizer.Add(self.page_sizers[-1], 1, wx.ALL|wx.EXPAND, 0)

        # Add the sizer for the top half.
        top_sizer = wx.BoxSizer(wx.VERTICAL)
        self.page_sizers[-1].Add(top_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Add the page to the top sizer.
        top_sizer.Add(panel, 1, wx.ALL|wx.EXPAND, 0)

        # Add the sizer for the wizard buttons.
        self.button_sizers.append(wx.BoxSizer(wx.HORIZONTAL))
        self.page_sizers[-1].Add(self.button_sizers[-1], 0, wx.ALIGN_RIGHT|wx.ALL, 0)

        # Store the apply button flag.
        self.button_apply.append(apply_button)


    def build_buttons(self):
        """Construct the buttons for all pages of the wizard."""

        # The number of pages.
        num_pages = len(self.pages)

        # Loop over each page.
        for i in range(num_pages):
            # The back button (only for multi-pages, after the first).
            if num_pages > 1 and i > 0:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, "Back")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.back, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Return to the previous page")
                self.button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self.go_back, button)

                # Spacer.
                self.button_sizers[i].AddSpacer(5)

            # The apply button.
            if self.button_apply[i]:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, "Apply")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.apply, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Apply the operation")
                self.button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self.pages[i].apply, button)

                # Spacer.
                self.button_sizers[i].AddSpacer(5)

            # The next button (only for multi-pages, excluding the last).
            if num_pages > 1 and i < num_pages - 1:
                # Create the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, "Next")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.next, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Move to the next page")
                self.button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self.go_forward, button)

                # Spacer.
                self.button_sizers[i].AddSpacer(5)

            # The OK button (only for single pages).
            if num_pages == 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, "OK")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.ok, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Accept the operation")
                self.button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self.pages[i].ok, button)

            # The finish button (only for the last page with multi-pages).
            if num_pages > 1 and i == num_pages - 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, "Finish")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.ok, wx.BITMAP_TYPE_ANY))
                button.SetToolTipString("Accept the operation")
                self.button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self.pages[i].ok, button)

            # Spacer.
            self.button_sizers[i].AddSpacer(15)

            # The cancel button.
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, "Cancel")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.cancel, wx.BITMAP_TYPE_ANY))
            button.SetToolTipString("Abort the operation")
            self.button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.pages[i].cancel, button)



    def display_page(self, i):
        """Display the given page.

        @param i:   The index of the page to display.
        @type i:    int
        """

        # Hide all of the original contents.
        for j in range(len(self.pages)):
            self.main_sizer.Hide(self.page_sizers[j])

        # Add the page.
        self.main_sizer.Add(self.page_sizers[i], 1, wx.ALL|wx.EXPAND, 0)

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()


    def run(self):
        """Execute the wizard."""

        # Build the buttons for the entire wizard.
        self.build_buttons()

        # Show the wizard.
        self.ShowModal()

        # Loop over the pages.
        for i in range(len(self.pages)):
            # Display the page.
            self.display_page(i)

        # Destroy the wizard.
        self.Destroy()
