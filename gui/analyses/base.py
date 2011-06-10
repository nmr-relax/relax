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

# relax GUI module imports.
from gui import paths


class Base_frame:
    """The base class for all frames."""

    # Hard coded variables.
    border = 10
    size_graphic_panel = 200
    spacer_horizontal = 5
    width_text = 240
    width_button = 100

    def add_button_open(self, box, parent, fn=None, width=-1, height=-1):
        """Add a button for opening and changing files and directories.

        @param box:         The box element to pack the control into.
        @type box:          wx.BoxSizer instance
        @param parent:      The parent GUI element.
        @type parent:       wx object
        @keyword fn:        The function or method to execute when clicking on the button.
        @type fn:           func
        @keyword width:     The minimum width of the control.
        @type width:        int
        @keyword height:    The minimum height of the control.
        @type height:       int
        """

        # The button.
        button = wx.Button(parent, -1, "Change")

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
        """

        # A horizontal sizer for the contents.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        label.SetMinSize((118, 17))
        label.SetFont(self.gui.font_normal)
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.BitmapButton(self.parent, -1, wx.Bitmap(paths.IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        button.SetSize(button.GetBestSize())
        self.gui.Bind(wx.EVT_BUTTON, method, button)
        sizer.Add(button, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALIGN_RIGHT, 0)


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
        field = control(parent, -1, text)

        # The font and control properties.
        field.SetMinSize((width, height))
        field.SetFont(self.gui.font_normal)
        field.SetEditable(editable)

        # Add the control to the box.
        box.Add(field, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Return the text field.
        return field


    def add_text_sel_element(self, box, parent, text="", default="", control=wx.TextCtrl, fn=None, editable=True, button=False):
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
        @keyword control:       The control class to use.
        @type control:          wx.TextCtrl derived class
        @keyword fn:            The function or method to execute when clicking on the button.  If this is a string, then an equivalent function will be searched for in the control object.
        @type fn:               func or str
        @keyword editable:      A flag specifying if the control is editable or not.
        @type editable:         bool
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
            self.add_button_open(sizer, parent, fn=fn, width=self.width_button, height=size_horizontal)

        # No button, so add a spacer.
        else:
            sizer.AddSpacer((self.width_button, -1))

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)

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


    def build_main_box(self, box):
        """Construct the highest level box to pack into the automatic analysis frames.

        @param box: The horizontal box element to pack the elements into.
        @type box:  wx.BoxSizer instance
        """

        # Build the left hand box and add to the main box.
        left_box = self.build_left_box()
        box.Add(left_box, 0, wx.ADJUST_MINSIZE, 0)

        # Central spacer.
        box.AddSpacer(self.border)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 1, wx.ALL|wx.EXPAND, 0)


    def setup_analysis_element(self, parent):
        """Set up the specific analysis GUI element.

        @param parent:  The parent GUI element.
        @type parent:   wx object
        @return:        The sizer object.
        @rtype:         wx.Sizer instance
        """

        # Some sizers.
        sizer_hori = wx.BoxSizer(wx.HORIZONTAL)
        sizer_vert = wx.BoxSizer(wx.VERTICAL)
        sizer_cent = wx.BoxSizer(wx.HORIZONTAL)

        # Pack the sizer into the frame.
        parent.SetSizer(sizer_hori)

        # Left and right borders.
        sizer_hori.AddSpacer(self.border)
        sizer_hori.Add(sizer_vert, 1, wx.EXPAND|wx.ALL)
        sizer_hori.AddSpacer(self.border)

        # Top and bottom borders.
        sizer_vert.AddSpacer(self.border)
        sizer_vert.Add(sizer_cent, 1, wx.EXPAND|wx.ALL)
        sizer_vert.AddSpacer(self.border)

        # Return the central sizer.
        return sizer_cent
