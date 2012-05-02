###############################################################################
#                                                                             #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.filedialog import RelaxFileDialog
from gui.fonts import font
from gui.icons import relax_icons
from gui.misc import add_border, bool_to_gui, gui_to_int, gui_to_str, int_to_gui, open_file, protected_exec, str_to_gui
from gui.message import Question
from gui import paths
from gui.wizard_elements import String_list, String_list_of_lists


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
    setup_fail = False
    size_button = (100, 33)
    size_square_button = (33, 33)
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

        # The wizard GUI element storage.
        self._elements = {}

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
        title.SetFont(font.title)

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


    def _free_file_format_reset(self, event):
        """Reset the free file format widget contents to the original values.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Ask a question.
        if status.show_gui and Question('Would you really like to reset the free file format settings?', parent=self).ShowModal() == wx.ID_NO:
            return

        # First reset.
        ds.relax_gui.free_file_format.reset()

        # Then update the values.
        self._free_file_format_set_vals()


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


    def _free_file_format_set_vals(self):
        """Set the free file format widget contents to the values from the relax data store."""

        # The column numbers.
        self.spin_id_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_id_col))
        self.mol_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.mol_name_col))
        self.res_num_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.res_num_col))
        self.res_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.res_name_col))
        self.spin_num_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_num_col))
        self.spin_name_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.spin_name_col))
        if hasattr(self, 'data_col'):
            self.data_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.data_col))
        if hasattr(self, 'err_col'):
            self.err_col.SetValue(int_to_gui(ds.relax_gui.free_file_format.err_col))

        # The column separator.
        if not ds.relax_gui.free_file_format.sep:
            self.sep.SetValue(str_to_gui("white space"))
        else:
            self.sep.SetValue(str_to_gui(ds.relax_gui.free_file_format.sep))


    def GetValue(self, key):
        """Special wizard method for getting the value of the GUI element corresponding to the key.

        @param key:     The key value of the desired GUI element.
        @type key:      str
        @return:        The value that the specific GUI element's GetValue() method returns.
        @rtype:         unknown
        """

        # Call the element's method.
        return self._elements[key].GetValue()


    def SetValue(self, key, value):
        """Special wizard method for setting the value of the GUI element corresponding to the key.

        @param key:     The key value of the desired GUI element.
        @type key:      str
        @param value:   The value that the specific GUI element's SetValue() method expects.
        @type value:    unknown
        """

        # Call the element's method.
        self._elements[key].SetValue(value)


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
        text.SetFont(font.normal)

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
        text.SetFont(font.normal)
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
        combo.SetFont(font.normal)
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
        text.SetFont(font.normal)
        sub_sizer.Add(text, 1, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sub_sizer.AddSpacer(10)

        # The choice element.
        type_choice = wx.Choice(self, -1, style=wx.ALIGN_LEFT, choices=choices)
        sub_sizer.Add(type_choice, 1, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)
        type_choice.SetFont(font.normal)
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
        text.SetFont(font.normal)
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
        combo.SetFont(font.normal)
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


    def element_string_list(self, key=None, sizer=None, desc=None, tooltip=None, divider=None, padding=0, spacer=None):
        """Set up the element and store it.

        @keyword key:       The dictionary key to store the element with.
        @type key:          str
        @keyword sizer:     The sizer to put the input field widget into.
        @type sizer:        wx.Sizer instance
        @keyword desc:      The text description.
        @type desc:         str
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        """

        # Create the element.
        element = String_list(name=key, parent=self, sizer=sizer, desc=desc, tooltip=tooltip, divider=divider, padding=padding, spacer=spacer)

        # Store it.
        self._elements[key] = element


    def element_string_list_of_lists(self, key=None, titles=None, sizer=None, desc=None, tooltip=None, divider=None, padding=0, spacer=None):
        """Set up the element and store it.

        @keyword key:       The dictionary key to store the element with.
        @type key:          str
        @keyword titles:    The titles of each of the elements of the fixed width second dimension.
        @type titles:       list of str
        @keyword sizer:     The sizer to put the input field widget into.
        @type sizer:        wx.Sizer instance
        @keyword desc:      The text description.
        @type desc:         str
        @keyword tooltip:   The tooltip which appears on hovering over the text or input field.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        """

        # Create the element.
        element = String_list_of_lists(name=key, titles=titles, parent=self, sizer=sizer, desc=desc, tooltip=tooltip, divider=divider, padding=padding, spacer=spacer)

        # Store it.
        self._elements[key] = element


    def file_selection(self, sizer, desc, message='File selection', wildcard=wx.FileSelectorDefaultWildcardStr, style=wx.FD_DEFAULT_STYLE, tooltip=None, divider=None, padding=0, spacer=None, preview=True):
        """Build the file selection element.

        @param sizer:       The sizer to put the input field into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword message:   The file selector prompt string.
        @type message:      String
        @keyword wildcard:  The file wildcard pattern.  For example for opening PDB files, this could be "PDB files (*.pdb)|*.pdb;*.PDB".
        @type wildcard:     String
        @keyword style:     The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:        long
        @keyword tooltip:   The tooltip which appears on hovering over all the GUI elements.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @keyword preview:   A flag which if true will allow the file to be previewed.
        @type preview:      bool
        @return:            The file selection GUI element.
        @rtype:             wx.TextCtrl
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        text.SetFont(font.normal)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The input field.
        if not hasattr(self, 'file_selection_field'):
            self.file_selection_field = []
        self.file_selection_field.append(wx.TextCtrl(self, -1, ''))
        field = self.file_selection_field[-1]
        field.SetMinSize((-1, self.height_element))
        field.SetFont(font.normal)
        sub_sizer.Add(field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # The file selection object.
        obj = RelaxFileDialog(self, field=field, message=message, wildcard=wildcard, style=style)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The file selection button.
        button = wx.BitmapButton(self, -1, wx.Bitmap(paths.icon_16x16.open, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((self.height_element, self.height_element))
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        self.Bind(wx.EVT_BUTTON, obj.select_event, button)

        # File preview.
        if not hasattr(self, 'file_selection_preview_button'):
            self.file_selection_preview_button = []
        if not preview:
            self.file_selection_preview_button.append(None)
        else:
            # A little spacing.
            sub_sizer.AddSpacer(5)

            # The preview button.
            self.file_selection_preview_button.append(wx.BitmapButton(self, -1, wx.Bitmap(paths.icon_16x16.document_preview, wx.BITMAP_TYPE_ANY)))
            button = self.file_selection_preview_button[-1]
            button.SetMinSize((self.height_element, self.height_element))
            sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
            self.Bind(wx.EVT_BUTTON, self.preview_file, button)

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


    def free_file_format(self, sizer, padding=10, spacer=3, data_cols=False, save=True, reset=True):
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
        @keyword reset:     A flag which if True will cause the reset button to be displayed.
        @type reset:        bool
        """

        # A static box to hold all the widgets.
        box = wx.StaticBox(self, -1, "Free format file settings")
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
        sizer.Add(border, 0, wx.EXPAND)
        sizer.AddStretchSpacer()

        # Calculate the divider position.
        divider = self._div_left - border.GetMinSize()[0] / 2 - padding

        # The columns.
        self.spin_id_col = self.input_field(field_sizer, "Spin ID column:", divider=divider, padding=padding, spacer=spacer)
        self.mol_name_col = self.input_field(field_sizer, "Molecule name column:", divider=divider, padding=padding, spacer=spacer)
        self.res_num_col = self.input_field(field_sizer, "Residue number column:", divider=divider, padding=padding, spacer=spacer)
        self.res_name_col = self.input_field(field_sizer, "Residue name column:", divider=divider, padding=padding, spacer=spacer)
        self.spin_num_col = self.input_field(field_sizer, "Spin number column:", divider=divider, padding=padding, spacer=spacer)
        self.spin_name_col = self.input_field(field_sizer, "Spin name column:", divider=divider, padding=padding, spacer=spacer)
        if data_cols:
            self.data_col = self.input_field(field_sizer, "Data column:", divider=divider, padding=padding, spacer=spacer)
            self.err_col = self.input_field(field_sizer, "Error column:", divider=divider, padding=padding, spacer=spacer)

        # The column separator.
        self.sep = self.combo_box(field_sizer, "Column separator:", ["white space", ",", ";", ":", ""], divider=divider, padding=padding, spacer=spacer, read_only=False)

        # Add the field sizer to the main sizer.
        main_sizer.Add(field_sizer, 1, wx.ALL|wx.EXPAND, 0)

        # Set the values.
        self._free_file_format_set_vals()

        # Buttons!
        if save or reset:
            # Add a save button.
            if save:
                # Build the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, "")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.save, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Save the free file format settings within the relax data store.")
                button.SetMinSize(self.size_square_button)

                # Add the button.
                button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

                # Padding.
                button_sizer.AddSpacer(padding)

                # Bind the click event.
                self.Bind(wx.EVT_BUTTON, self._free_file_format_save, button)

            # Add a reset button.
            if reset:
                # Build the button.
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, "")
                button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.edit_delete, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Reset the free file format settings to the original values.")
                button.SetMinSize(self.size_square_button)

                # Add the button.
                button_sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

                # Bind the click event.
                self.Bind(wx.EVT_BUTTON, self._free_file_format_reset, button)

            # Add the button sizer to the widget (with spacing).
            main_sizer.AddSpacer(padding)
            main_sizer.Add(button_sizer, 0, wx.ALL, 0)


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
        text.SetFont(font.normal)
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
        field.SetFont(font.normal)
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

        This method will be called when clicking on the apply button.
        """


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


    def on_init(self):
        """To be over-ridden if an action is to be performed when a page is newly displayed.

        This method will be called by the wizard class method _display_page() at the very end.
        """


    def on_next(self):
        """To be over-ridden if an action is to be performed just before moving to the next page.

        This method is called when moving to the next page of the wizard.
        """


    def preview_file(self, event):
        """Preview a file.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Find the correct button.
        button = event.GetEventObject()
        index = None
        for i in range(len(self.file_selection_preview_button)):
            if button == self.file_selection_preview_button[i]:
                index = i
                break

        # No match.
        if index == None:
            return

        # The file name.
        file = gui_to_str(self.file_selection_field[index].GetValue())

        # No file, so do nothing.
        if file == None:
            return

        # Open the file as text.
        open_file(file, force_text=True)


    def spin_control(self, sizer, desc, default='', min=0, max=100, tooltip=None, divider=None, padding=0, spacer=None):
        """Build the spin control widget.

        @param sizer:       The sizer to put the spin control widget into.
        @type sizer:        wx.Sizer instance
        @param desc:        The text description.
        @type desc:         str
        @keyword default:   The default value of the control.
        @type default:      int
        @keyword min:       The minimum value allowed.
        @type min:          int
        @keyword max:       The maximum value allowed.
        @type max:          int
        @keyword tooltip:   The tooltip which appears on hovering over the text or spin control.
        @type tooltip:      str
        @keyword divider:   The optional position of the divider.  If None, the class variable _div_left will be used.
        @type divider:      None or int
        @keyword padding:   Spacing to the left and right of the widgets.
        @type padding:      int
        @keyword spacer:    The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:       None or int
        @return:            The spin control object.
        @rtype:             wx.TextCtrl instance
        """

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(self, -1, desc, style=wx.ALIGN_LEFT)
        text.SetFont(font.normal)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            divider = self._div_left

        # Spacing.
        x, y = text.GetSize()
        sub_sizer.AddSpacer((divider - x, 0))

        # The spin control.
        field = wx.SpinCtrl(self, id=-1, initial=default, min=min, max=max)
        field.SetMinSize((50, self.height_element))
        field.SetFont(font.normal)
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
        text.SetFont(font.normal)
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
        field.SetFont(font.normal)
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
        text.SetFont(font.normal)
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
        text.SetFont(font.normal)
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
    ICON_APPLY = paths.icon_22x22.dialog_ok_apply
    ICON_BACK = paths.icon_22x22.go_previous_view
    ICON_CANCEL = paths.icon_22x22.dialog_cancel
    ICON_FINISH = paths.icon_22x22.dialog_ok
    ICON_NEXT = paths.icon_22x22.go_next_view
    ICON_OK = paths.icon_22x22.dialog_ok
    ICON_SKIP = paths.icon_22x22.skip
    TEXT_APPLY = " Apply"
    TEXT_BACK = " Back"
    TEXT_CANCEL = " Cancel"
    TEXT_FINISH = " Finish"
    TEXT_NEXT = " Next"
    TEXT_OK = " OK"
    TEXT_SKIP = " Skip"


    def __init__(self, parent=None, size_x=400, size_y=400, title='', border=10, style=wx.DEFAULT_DIALOG_STYLE):
        """Set up the window.

        @keyword parent:    The parent window.
        @type parent:       wx.Window instance
        @keyword size_x:    The width of the wizard.
        @type size_x:       int
        @keyword size_y:    The height of the wizard.
        @type size_y:       int
        @keyword title:     The title of the wizard dialog.
        @type title:        str
        @keyword border:    The size of the border inside the wizard.
        @type border:       int
        @keyword style:     The dialog style.
        @type style:        wx style
        """

        # Store the args.
        self._size_x = size_x
        self._size_y = size_y
        self._border = border

        # Execute the base class method.
        wx.Dialog.__init__(self, parent, id=-1, title=title, style=style)

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
        self._uf_flush = []
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

            # No user function flushing of the GUI interpreter thread prior to proceeding.
            self._uf_flush.append(False)

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
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_BACK)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_BACK, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
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
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_APPLY)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_APPLY, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
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
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_SKIP)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_SKIP, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
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
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_NEXT)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_NEXT, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Move to the next page")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._go_next, button)
                self._buttons[i]['next'] = button

            # The OK button (only for single pages).
            if self._num_pages == 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_OK)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_OK, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Accept the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._ok, button)
                self._buttons[i]['ok'] = button

            # The finish button (only for the last page with multi-pages).
            if self._num_pages > 1 and i == self._num_pages - 1:
                button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_FINISH)
                button.SetBitmapLabel(wx.Bitmap(self.ICON_FINISH, wx.BITMAP_TYPE_ANY))
                button.SetFont(font.normal)
                button.SetToolTipString("Accept the operation")
                button.SetMinSize(self._size_button)
                self._button_sizers[i].Add(button, 0, wx.ADJUST_MINSIZE, 0)
                self.Bind(wx.EVT_BUTTON, self._ok, button)
                self._buttons[i]['finish'] = button

            # Spacer.
            self._button_sizers[i].AddSpacer(15)

            # The cancel button.
            button = buttons.ThemedGenBitmapTextButton(self, -1, None, self.TEXT_CANCEL)
            button.SetBitmapLabel(wx.Bitmap(self.ICON_CANCEL, wx.BITMAP_TYPE_ANY))
            button.SetFont(font.normal)
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

        # Close the window.
        self.Close()


    def _display_page(self, i):
        """Display the given page.

        @param i:   The index of the page to display.
        @type i:    int
        """

        # Hide all of the original contents.
        for j in range(self._num_pages):
            if self._main_sizer.IsShown(self._page_sizers[j]):
                self._main_sizer.Hide(self._page_sizers[j])

        # Show the desired page.
        if status.show_gui:
            self._main_sizer.Show(self._page_sizers[i])

        # Execute the page's on_display() method.
        self._pages[i].on_display()
        self._pages[i].on_display_post()

        # Re-perform the window layout.
        self.Layout()
        self.Refresh()

        # Execute the page's on_init() method.
        self._pages[i].on_init()


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

                # UF flush.
                if self._uf_flush[self._current_page]:
                    interpreter.flush()

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

                # UF flush.
                if self._uf_flush[i]:
                    interpreter.flush()

                # Check for execution errors.
                if not self._pages[self._current_page].exec_status:
                    # Do not proceed.
                    if not self._proceed_on_error[self._current_page]:
                        return

                # Increment the execution counter.
                self._exec_count[i] += 1

        # Then close the dialog.
        if self.IsModal():
            self.EndModal(wx.ID_OK)
        else:
            self.Close()


    def _seq_loop(self):
        """Loop over the sequence in the forwards direction."""

        # Initialise.
        current = 0

        # First yield the initial element (always zero!).
        yield current

        # Loop over the sequence.
        while True:
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


    def add_page(self, panel, apply_button=True, skip_button=False, exec_on_next=True, proceed_on_error=True, uf_flush=False):
        """Add a new page to the wizard.

        @param panel:               The page to add to the wizard.
        @type panel:                wx.Panel instance
        @keyword apply_button:      A flag which if true will show the apply button for that page.
        @type apply_button:         bool
        @keyword skip_button:       A flag which if true will show the skip button for that page.
        @type skip_button:          bool
        @keyword exec_on_next:      A flag which if true will run the on_execute() method when clicking on the next button.
        @type exec_on_next:         bool
        @keyword proceed_on_error:  A flag which if True will proceed to the next page (or quit if there are no more pages) despite the occurrence of an error in execution.  If False, the page will remain open (the GUI interpreter thread will be flushed first to synchronise).
        @type proceed_on_error:     bool
        @keyword uf_flush:          A flag which if True will cause the GUI interpreter thread to be flushed to clear out all user function call prior to proceeding.
        @type uf_flush:             bool
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
        if not proceed_on_error or uf_flush:
            self._uf_flush[index] = True

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

        # Check that all pages have been set up correctly, returning without doing anything if not.
        for i in range(self._num_pages):
            if self._pages[i].setup_fail:
                return

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
            wiz_status = self.ShowModal()

            # Return the status.
            return wiz_status

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
