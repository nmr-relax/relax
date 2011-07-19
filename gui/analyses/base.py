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
import wx
from wx.lib import buttons

# relax module imports.
from generic_fns.mol_res_spin import count_spins
from generic_fns.pipes import cdp_name

# relax GUI module imports.
from gui import paths
from gui.misc import str_to_gui


class Base_frame:
    """The base class for all frames."""

    # Hard coded variables.
    border = 10
    size_graphic_panel = 200
    spacer_horizontal = 5
    width_text = 240
    width_button = 100

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
        """

        # The button.
        button = buttons.ThemedGenBitmapTextButton(parent, -1, None, str_to_gui(text))
        button.SetBitmapLabel(wx.Bitmap(icon, wx.BITMAP_TYPE_ANY))

        # The font and button properties.
        button.SetMinSize((width, height))
        button.SetFont(self.gui.font_normal)

        # Bind the click.
        self.gui.Bind(wx.EVT_BUTTON, fn, button)

        # Add the button to the box.
        box.Add(button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)


    def add_execute_relax(self, box, method):
        """Create and add the relax execution GUI element to the given box.

        @param box:     The box element to pack the relax execution GUI element into.
        @type box:      wx.BoxSizer instance
        @param method:  The method to execute when the button is clicked.
        @type method:   method
        @return:        The unique ID of the button.
        @rtype:         int
        """

        # A horizontal sizer for the contents.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # A unique ID.
        id = wx.NewId()

        # The button.
        button = buttons.ThemedGenBitmapTextButton(self.parent, id, None, " Execute relax")
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        self.gui.Bind(wx.EVT_BUTTON, method, button)
        sizer.Add(button, 0, wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALIGN_RIGHT, 0)

        # Return the ID.
        return id


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
        field.SetFont(self.gui.font_normal)

        # Add the control to the box.
        box.Add(field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Return the text field.
        return field


    def add_spin_element(self, box, parent, text="", default=0, min=0, max=1000, tooltip=None, control=wx.SpinCtrl):
        """Create a text selection element using a spinner for the frame.

        This consists of a horizontal layout with a static text element and a spin control

        @param box:             The box element to pack the structure file selection GUI element into.
        @type box:              wx.BoxSizer instance
        @param parent:          The parent GUI element.
        @type parent:           wx object
        @keyword text:          The static text.
        @type text:             str
        @keyword default:       The default value of the control.
        @type default:          str
        @keyword min:           The minimum value allowed.
        @type min:              int
        @keyword max:           The maximum value allowed.
        @type max:              int
        @keyword tooltip:   	The tooltip which appears on hovering over the text or spin control.
        @type tooltip:      	str
        @keyword control:       The control class to use.
        @type control:          wx.SpinCtrl derived class
        @return:                The text control object.
        @rtype:                 control object
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = self.add_static_text(sizer, parent, text=text, width=self.width_text)

        # The size for all elements, based on this text.
        size = label.GetSize()
        size_horizontal = size[1] + 8

        # Spacer.
        sizer.AddSpacer((self.spacer_horizontal, -1))

        # The text input field.
        field = self.add_spin_control(sizer, parent, text=default, control=control, min=min, max=max, height=size_horizontal)

        # Spacer.
        sizer.AddSpacer((self.spacer_horizontal, -1))

        # No button, so add a spacer.
        sizer.AddSpacer((self.width_button, -1))

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Tooltip.
        if tooltip:
            label.SetToolTipString(tooltip)
            field.SetToolTipString(tooltip)

        # Return the text control object.
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
        self.spin_systems = self.add_text_sel_element(box, self.parent, text="Spin systems", button_text=" Spin editor", default=self.spin_count(), icon=paths.icon_16x16.spin, fn=self.launch_spin_editor, editable=False, button=True)


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
        label.SetFont(self.gui.font_normal)

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
        label = wx.StaticText(self.parent, -1, text)

        # The font properties.
        label.SetFont(self.gui.font_subtitle)

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
        label = wx.StaticText(self.parent, -1, text)

        # The font properties.
        label.SetFont(self.gui.font_normal)

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
        field.SetFont(self.gui.font_normal)

        # Editable (change the colour if not).
        field.SetEditable(editable)
        if not editable:
            colour = self.parent.GetBackgroundColour()
            field.SetOwnBackgroundColour(colour)

        # Add the control to the box.
        box.Add(field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Return the text field.
        return field


    def add_text_sel_element(self, box, parent, text="", default="", tooltip=None, button_text=" Change", control=wx.TextCtrl, icon=paths.icon_16x16.open, fn=None, editable=True, button=False):
        """Create a text selection element for the frame.

        This consists of a horizontal layout with a static text element, a text control, and an optional button.

        @param box:             The box element to pack the structure file selection GUI element into.
        @type box:              wx.BoxSizer instance
        @param parent:          The parent GUI element.
        @type parent:           wx object
        @keyword text:          The static text.
        @type text:             str
        @keyword default:       The default text of the control.
        @type default:          str
        @keyword tooltip:   	The tooltip which appears on hovering over the text or input field.
        @type tooltip:      	str
        @keyword button_text:   The text to display on the button.
        @type button_text:      str
        @keyword control:       The control class to use.
        @type control:          wx.TextCtrl derived class
        @keyword icon:          The path of the icon to use for the button.
        @type icon:             str
        @keyword fn:            The function or method to execute when clicking on the button.  If this is a string, then an equivalent function will be searched for in the control object.
        @type fn:               func or str
        @keyword editable:      A flag specifying if the control is editable or not.
        @type editable:         bool
        @keyword button:        A flag which if True will cause a button to appear.
        @type button:           bool
        @return:                The text control object.
        @rtype:                 control object
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = self.add_static_text(sizer, parent, text=text, width=self.width_text)

        # The size for all elements, based on this text.
        size = label.GetSize()
        size_horizontal = size[1] + 8

        # Spacer.
        sizer.AddSpacer((self.spacer_horizontal, -1))

        # The text input field.
        field = self.add_text_control(sizer, parent, text=default, control=control, height=size_horizontal, editable=editable)

        # Spacer.
        sizer.AddSpacer((self.spacer_horizontal, -1))

        # The button.
        if button:
            # Function is in the control class.
            if type(fn) == str:
                # The function.
                fn = getattr(field, fn)

            # Add the button.
            button_open = self.add_button_open(sizer, parent, icon=icon, text=button_text, fn=fn, width=self.width_button, height=size_horizontal)

        # No button, so add a spacer.
        else:
            sizer.AddSpacer((self.width_button, -1))

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Tooltip.
        if tooltip:
            label.SetToolTipString(tooltip)
            field.SetToolTipString(tooltip)
	    if button:
            	button_open.SetToolTipString(tooltip)

        # Return the text control object.
        return field


    def add_title(self, box, text):
        """Create and add the frame title.

        @param box:     The box element to pack the frame title into.
        @type box:      wx.BoxSizer instance
        @param text:    The text of the title.
        @type text:     str
        """

        # The title.
        label = wx.StaticText(self.parent, -1, text)

        # The font properties.
        label.SetFont(self.gui.font_title)

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
            bitmap = wx.StaticBitmap(self.parent, -1, wx.Bitmap(bitmaps[i], wx.BITMAP_TYPE_ANY))

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
        box.AddSpacer(self.border)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 1, wx.ALL|wx.EXPAND, 0)


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
