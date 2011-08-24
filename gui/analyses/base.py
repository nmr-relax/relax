###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
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
"""Module containing the base class for all frames."""

# Python module imports.
from os import sep
import wx
from wx.lib import buttons

# relax module imports.
from generic_fns.mol_res_spin import count_spins
from generic_fns.pipes import cdp_name

# relax GUI module imports.
from gui import paths
from gui.analyses.elements import Text_ctrl
from gui.fonts import font
from gui.misc import add_border, int_to_gui, str_to_gui
from gui.user_functions.base import UF_page


class Base_analysis(wx.lib.scrolledpanel.ScrolledPanel):
    """The base class for all frames."""

    # Hard coded variables.
    border = 10
    size_graphic_panel = 200
    spacer_horizontal = 5
    width_text = 240
    width_button = 100
    width_main_separator = 40

    def __init__(self, parent, id=wx.ID_ANY, pos=None, size=None, style=None, name=None, gui=None):
        """Initialise the scrolled window.

        @param parent:  The parent wx element.
        @type parent:   wx object
        @keyword id:    The unique ID number.
        @type id:       int
        @keyword pos:   The position.
        @type pos:      wx.Size object
        @keyword size:  The size.
        @type size:     wx.Size object
        @keyword style: The style.
        @type style:    int
        @keyword name:  The name for the panel.
        @type name:     unicode
        """

        # Execute the base class method.
        super(Base_analysis, self).__init__(parent, id=id, pos=pos, size=size, style=style, name=name)

        # Determine the size of the scrollers.
        self.width_vscroll = wx.SystemSettings_GetMetric(wx.SYS_VSCROLL_X)

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(box_main)

        # Build the central sizer, with borders.
        box_centre = add_border(box_main, border=self.border, packing=wx.HORIZONTAL)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        self.build_main_box(box_centre)

        # Set up the scrolled panel.
        self.SetAutoLayout(True)
        self.SetupScrolling(scroll_x=False, scroll_y=True)

        # Bind resize events.
        self.Bind(wx.EVT_SIZE, self.resize)


    def add_button_open(self, box, parent, icon=paths.icon_16x16.open, text=" Change", fn=None, width=-1, height=-1):
        """Add a button for opening and changing files and directories.

        @param box:         The box element to pack the control into.
        @type box:          wx.BoxSizer instance
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword icon:      The path of the icon to use for the button.
        @type icon:         str
        @keyword text:      The text to display on the button.
        @type text:         str
        @keyword fn:        The function or method to execute when clicking on the button.
        @type fn:           func
        @keyword width:     The minimum width of the control.
        @type width:        int
        @keyword height:    The minimum height of the control.
        @type height:       int
        @return:            The button.
        @rtype:             wx.lib.buttons.ThemedGenBitmapTextButton instance
        """

        # The button.
        button = buttons.ThemedGenBitmapTextButton(parent, -1, None, str_to_gui(text))
        button.SetBitmapLabel(wx.Bitmap(icon, wx.BITMAP_TYPE_ANY))

        # The font and button properties.
        button.SetMinSize((width, height))
        button.SetFont(font.normal)

        # Bind the click.
        self.gui.Bind(wx.EVT_BUTTON, fn, button)

        # Add the button to the box.
        box.Add(button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Return the button.
        return button


    def add_execute_relax(self, box, method):
        """Create and add the relax execution GUI element to the given box.

        @param box:     The box element to pack the relax execution GUI element into.
        @type box:      wx.BoxSizer instance
        @param method:  The method to execute when the button is clicked.
        @type method:   method
        @return:        The button.
        @rtype:         wx.lib.buttons.ThemedGenBitmapTextButton instance
        """

        # A horizontal sizer for the contents.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # A unique ID.
        id = wx.NewId()

        # The button.
        button = buttons.ThemedGenBitmapTextButton(self, id, None, " Execute relax")
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        self.gui.Bind(wx.EVT_BUTTON, method, button)
        sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALIGN_RIGHT, 0)

        # Return the button.
        return button


    def add_spin_control(self, box, parent, text='', min=None, max=None, control=wx.SpinCtrl, width=-1, height=-1):
        """Add a text control field to the box.

        @param box:         The box element to pack the control into.
        @type box:          wx.BoxSizer instance
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword text:      The default text of the control.
        @type text:         str
        @keyword min:       The minimum value allowed.
        @type min:          int
        @keyword max:       The maximum value allowed.
        @type max:          int
        @keyword control:   The control class to use.
        @type control:      wx.TextCtrl derived class
        @keyword width:     The minimum width of the control.
        @type width:        int
        @keyword height:    The minimum height of the control.
        @type height:       int
        @return:            The text control object.
        @rtype:             control object
        """

        # The control.
        field = control(parent, -1, text, min=min, max=max)

        # The font and control properties.
        field.SetMinSize((width, height))
        field.SetFont(font.normal)

        # Add the control to the box.
        box.Add(field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Return the text field.
        return field


    def add_spin_systems(self, box, parent):
        """Add a special control for spin systems.

        Only one of these per analysis are allowed.

        @param box:         The box element to pack the control into.
        @type box:          wx.BoxSizer instance
        @param parent:      The parent GUI element.
        @type parent:       wx object
        """

        # Add the element.
        self.spin_systems = Text_ctrl(box, self, text="Spin systems", button_text=" Spin editor", default=self.spin_count(), icon=paths.icon_16x16.spin, fn=self.launch_spin_editor, editable=False, button=True, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)


    def add_static_text(self, box, parent, text='', width=-1, height=-1):
        """Add a text control field to the box.

        @param box:         The box element to pack the control into.
        @type box:          wx.BoxSizer instance
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword text:      The default text of the control.
        @type text:         str
        @keyword width:     The minimum width of the control.
        @type width:        int
        @keyword height:    The minimum height of the control.
        @type height:       int
        @return:            The label.
        @rtype:             wx.StaticText instance
        """

        # The label.
        label = wx.StaticText(parent, -1, text)

        # The font and label properties.
        label.SetMinSize((width, height))
        label.SetFont(font.normal)

        # Add the label to the box.
        box.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Return the label.
        return label


    def add_subtitle(self, box, text):
        """Create and add the subtitle.

        @param box:     The box element to pack the subtitle into.
        @type box:      wx.BoxSizer instance
        @param text:    The text of the subtitle.
        @type text:     str
        """

        # The title.
        label = wx.StaticText(self, -1, text)

        # The font properties.
        label.SetFont(font.subtitle)

        # Add the subtitle to the box, with spacing.
        box.AddSpacer(20)
        box.Add(label)
        box.AddSpacer(5)


    def add_subsubtitle(self, box, text):
        """Create and add the subsubtitle.

        @param box:     The box element to pack the text into.
        @type box:      wx.BoxSizer instance
        @param text:    The text of the subsubtitle.
        @type text:     str
        """

        # The text.
        label = wx.StaticText(self, -1, text)

        # The font properties.
        label.SetFont(font.normal)

        # Add the text to the box, with spacing.
        box.AddSpacer(10)
        box.Add(label)


    def add_text_control(self, box, parent, text='', control=wx.TextCtrl, width=-1, height=-1, editable=True):
        """Add a text control field to the box.

        @param box:         The box element to pack the control into.
        @type box:          wx.BoxSizer instance
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword text:      The default text of the control.
        @type text:         str
        @keyword control:   The control class to use.
        @type control:      wx.TextCtrl derived class
        @keyword width:     The minimum width of the control.
        @type width:        int
        @keyword height:    The minimum height of the control.
        @type height:       int
        @keyword editable:  A flag specifying if the control is editable or not.
        @type editable:     bool
        @return:            The text control object.
        @rtype:             control object
        """

        # The control.
        field = control(parent, -1, str_to_gui(text))

        # The font and control properties.
        field.SetMinSize((width, height))
        field.SetFont(font.normal)

        # Editable (change the colour if not).
        field.SetEditable(editable)
        if not editable:
            colour = self.GetBackgroundColour()
            field.SetOwnBackgroundColour(colour)

        # Add the control to the box.
        box.Add(field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Return the text field.
        return field


    def add_title(self, box, text):
        """Create and add the frame title.

        @param box:     The box element to pack the frame title into.
        @type box:      wx.BoxSizer instance
        @param text:    The text of the title.
        @type text:     str
        """

        # The title.
        label = wx.StaticText(self, -1, text)

        # The font properties.
        label.SetFont(font.title)

        # Pack the title, with spacing.
        box.AddSpacer(10)
        box.Add(label)
        box.AddSpacer(5)


    def build_left_box(self):
        """Construct the left hand box to pack into the automatic Rx analysis frame.

        @return:    The left hand box element containing the bitmap.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Convert the bitmap names to a list.
        if type(self.bitmap) != list:
            bitmaps = [self.bitmap]
        else:
            bitmaps = self.bitmap

        # Add the bitmaps.
        for i in range(len(bitmaps)):
            # The bitmap.
            bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(bitmaps[i], wx.BITMAP_TYPE_ANY))

            # Add it.
            box.Add(bitmap, 0, wx.ADJUST_MINSIZE, 10)

        # Return the box.
        return box


    def build_main_box(self, box):
        """Construct the highest level box to pack into the automatic analysis frames.

        @param box: The horizontal box element to pack the elements into.
        @type box:  wx.BoxSizer instance
        """

        # Build the left hand box and add to the main box.
        left_box = self.build_left_box()
        box.Add(left_box, 0, wx.ALL|wx.EXPAND|wx.ADJUST_MINSIZE, 0)

        # Central spacer.
        box.AddSpacer(self.width_main_separator)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 1, wx.ALL|wx.EXPAND, 0)


    def launch_spin_editor(self, event):
        """The spin editor GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Show the molecule, residue, and spin tree window.
        self.gui.show_tree(None)


    def resize(self, event):
        """The spin editor GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the virtual size to have the width of the visible size and the height of the virtual size.
        x = self.GetSize()[0] - self.width_vscroll
        y = self.GetVirtualSize()[1]
        self.SetVirtualSize((x, y))


    def spin_count(self):
        """Count the number of loaded spins, returning a string formatted as 'xxx spins loaded'.

        @return:    The number of loaded spins in the format 'xxx spins loaded'.
        @rtype:     str
        """

        # The data pipe.
        if hasattr(self.data, 'pipe_name'):
            pipe = self.data.pipe_name
        else:
            pipe = cdp_name()

        # The count.
        num = count_spins(pipe=pipe)

        # Return the formatted string.
        return "%s spins loaded and selected" % num


    def update_spin_count(self):
        """Update the spin count."""

        # Set the new value.
        self.spin_systems.SetValue(str_to_gui(self.spin_count()))



class Spectral_error_type_page(UF_page):
    """The NOE peak intensity reading wizard page for specifying the type of error to be used."""

    # Class variables.
    image_path = paths.WIZARD_IMAGE_PATH + 'spectrum' + sep + 'spectrum_200.png'
    uf_path = ['spectrum', 'error_analysis']
    height_desc = 450

    def add_contents(self, sizer):
        """Add the specific GUI elements.

        @param sizer:   A sizer object.
        @type sizer:    wx.Sizer instance
        """

        # Intro text.
        msg = "Please specify from where the peak intensity errors will be obtained.  The execution of the spectrum.error_analysis user function, as described above, will be postponed until after clicking on the 'Execute relax' button at the end of the automatic NOE analysis page."
        text = wx.StaticText(self, -1, msg)
        text.Wrap(self._main_size)
        sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sizer.AddStretchSpacer()

        # A box sizer for placing the box sizer in.
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(sizer2, 1, wx.ALL|wx.EXPAND, 0)

        # Bottom spacing.
        sizer.AddStretchSpacer()

        # A bit of indentation.
        sizer2.AddStretchSpacer()

        # A vertical sizer for the radio buttons.
        sizer_radio = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(sizer_radio, 1, wx.ALL|wx.EXPAND, 0)

        # The RMSD radio button.
        self.radio_rmsd = wx.RadioButton(self, -1, "Baseplane RMSD.")
        sizer_radio.Add(self.radio_rmsd, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spacing.
        sizer_radio.AddSpacer(10)

        # The replicated spectra radio button.
        self.radio_repl = wx.RadioButton(self, -1, "Replicated spectra.")
        sizer_radio.Add(self.radio_repl, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # Bind the buttons.
        self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_rmsd)
        self.Bind(wx.EVT_RADIOBUTTON, self._on_select, self.radio_repl)

        # Right side spacing.
        sizer2.AddStretchSpacer(3)

        # Bottom spacing.
        sizer.AddStretchSpacer()

        # Set the default selection.
        self.selection = 'rmsd'


    def _on_select(self, event):
        """Handle the radio button switching.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The button.
        button = event.GetEventObject()

        # RMSD.
        if button == self.radio_rmsd:
            self.selection = 'rmsd'
        elif button == self.radio_repl:
            self.selection = 'repl'
