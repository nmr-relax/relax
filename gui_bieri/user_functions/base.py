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
"""Base class module for the user function GUI elements."""

# Python module imports.
import wx
from wx.lib import buttons

# relax module imports.
from relax_errors import AllRelaxErrors, RelaxImplementError

# relax GUI module imports.
from gui_bieri.controller import Redirect_text
from gui_bieri.filedialog import openfile
from gui_bieri.message import error_message
from gui_bieri import paths


class File_selector:
    """Class for handling file selection dialogs and updating the respective fields."""

    def __init__(self, field):
        """Setup the class and store the field.

        @param field:   The field to update with the file selection.
        @type field:    wx.TextCtrl instance
        """

        # Store the args.
        self.field = field


    def select(self, event):
        """The script user function GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Open the file selection dialog.
        file = openfile(msg='Select the relax script to execute', default='relax scripts (*.py)|*.py')

        # Check the file.
        if not file:
            return

        # Update the field.
        self.field.SetValue(file)

        # Scroll the text to the end.
        self.field.SetInsertionPoint(len(file))



class UF_base:
    """User function GUI element base class."""

    def __init__(self, gui, interpreter):
        """Set up the user function class."""

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # Specific set up.
        self.setup()


    def setup(self):
        """Dummy method to be overwritten."""



class UF_window(wx.Dialog):
    """User function window GUI element base class.

    To inherit from this class, you must supply the add_uf() and execute() methods.  The add_uf() method should build the GUI elements specific to the user function, which the execute() method runs the user function.
    """

    # Some class variables.
    art_spacing = 20
    size_x = 600
    size_y = 400
    border = 10
    button_apply = True
    button_cancel = True
    button_ok = True
    divider = None
    frame_title = ''
    image_path = None
    input_size = 27
    main_text = ''
    title = ''

    def __init__(self, gui, interpreter, style=wx.DEFAULT_DIALOG_STYLE):
        """Set up the user function class."""

        # Store the args.
        self.gui = gui
        self.interpreter = interpreter

        # Execute the base class method.
        wx.Dialog.__init__(self, None, id=-1, title=self.frame_title, style=style)

        # Set up the frame.
        sizer = self.setup_frame()

        # Add the central part.
        centre_sizer = self.build_central_section(sizer)

        # Add the final buttons.
        self.add_buttons(sizer)

        # Add the artwork.
        self.add_artwork(centre_sizer)

        # The size of the image.
        image_x, image_y = self.image.GetSize()

        # Calculate the size of the main section, and the subdivisions.
        self.main_size = self.size_x - image_x - self.art_spacing - 2*self.border
        if self.divider:
            self.div_left = self.divider
            self.div_right = self.main_size - self.divider
        else:
            self.div_left = self.div_right = self.main_size / 2

        # Add the main sizer.
        main_sizer = self.build_main_section(centre_sizer)

        # Add the title.
        self.add_title(main_sizer)

        # Add the description.
        self.add_desc(main_sizer)

        # Add the user function specific GUI elements (bounded by spacers).
        main_sizer.AddStretchSpacer()
        self.add_uf(main_sizer)
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


    def add_buttons(self, sizer):
        """Add the buttons to the sizer.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Create a horizontal layout for the buttons.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT|wx.ALL, 0)

        # The apply button.
        if self.button_apply:
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, "Apply")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.apply, wx.BITMAP_TYPE_ANY))
            button.SetToolTipString("Apply the user function")
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.apply, button)

            # Spacer.
            button_sizer.AddSpacer(5)

        # The OK button.
        if self.button_ok:
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, "OK")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.ok, wx.BITMAP_TYPE_ANY))
            button.SetToolTipString("Accept the user function")
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.ok, button)

            # Spacer.
            button_sizer.AddSpacer(15)

        # The cancel button.
        if self.button_cancel:
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, "Cancel")
            button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.cancel, wx.BITMAP_TYPE_ANY))
            button.SetToolTipString("Abort the user function")
            button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)
            self.Bind(wx.EVT_BUTTON, self.cancel, button)


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


    def add_uf(self, sizer):
        """Add the user function specific GUI elements (dummy method).

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        raise RelaxImplementError


    def apply(self, event):
        """Apply the user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the user function.
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
        """Cancel the user function.

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


    def combo_box(self, sizer, desc, choices, evt_fn=None, divider=None, padding=0, spacer=None):
        """Build the combo box widget for list selections.

        @param sizer:       The sizer to put the combo box widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @param choices:     The list of choices.
        @type choices:      list of str
        @param evt_fn:      The event handling function.
        @type evt_fn:       func
        @keyword divider:   The optional position of the divider.  If None, the class variable div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
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
        combo = wx.ComboBox(self, -1, value='', style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=choices)
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

        # Return the combo box element.
        return combo


    def execute(self):
        """Execute the user function (dummy method)."""

        raise RelaxImplementError


    def file_selection(self, sizer, desc):
        """Build the file selection element.

        @param sizer:   The sizer to put the input field into.
        @type sizer:    wx.Sizer instance
        @param desc:    The text description.
        @type desc:     str
        @return:        The file selection GUI element.
        @rtype:         wx.TextCtrl
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
        obj = File_selector(field)

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


    def free_file_format(self, sizer, data_cols=False):
        """Build the free format file settings widget.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
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
        spin_id_col = self.input_field(sub_sizer, "Spin ID column:", divider=divider, padding=padding, spacer=spacer)
        mol_name_col = self.input_field(sub_sizer, "Molecule name column:", divider=divider, padding=padding, spacer=spacer)
        res_num_col = self.input_field(sub_sizer, "Residue number column:", divider=divider, padding=padding, spacer=spacer)
        res_name_col = self.input_field(sub_sizer, "Residue name column:", divider=divider, padding=padding, spacer=spacer)
        spin_num_col = self.input_field(sub_sizer, "Spin number column:", divider=divider, padding=padding, spacer=spacer)
        spin_name_col = self.input_field(sub_sizer, "Spin name column:", divider=divider, padding=padding, spacer=spacer)
        if data_cols:
            data_col = self.input_field(sub_sizer, "Data column:", divider=divider, padding=padding, spacer=spacer)
            err_col = self.input_field(sub_sizer, "Error column:", divider=divider, padding=padding, spacer=spacer)

        # The column separator.
        sep = self.combo_box(sub_sizer, "Column separator:", ["white space", "','", ""], divider=divider, padding=padding, spacer=0)

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

        # Return the field element.
        if data_cols:
            return spin_id_col, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, err_col, sep
        else:
            return spin_id_col, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep


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
        """Accept the user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execute the apply method.
        self.apply(event)

        # Then close.
        self.Close()


    def setup_frame(self):
        """Set up the generic user function frame.

        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Some sizers.
        sizer_hori = wx.BoxSizer(wx.HORIZONTAL)
        sizer_vert = wx.BoxSizer(wx.VERTICAL)
        sizer_cent = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(sizer_hori)

        # Set the default size of the controller.
        self.SetSize((self.size_x, self.size_y))

        # Left and right borders.
        sizer_hori.AddSpacer(self.border)
        sizer_hori.Add(sizer_vert, 1, wx.EXPAND|wx.ALL)
        sizer_hori.AddSpacer(self.border)

        # Top and bottom borders.
        sizer_vert.AddSpacer(self.border)
        sizer_vert.Add(sizer_cent, 1, wx.EXPAND|wx.ALL)
        sizer_vert.AddSpacer(self.border)

        # Centre the frame.
        self.Centre()

        # Return the sizer.
        return sizer_cent


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
