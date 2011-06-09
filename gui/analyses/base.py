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


class Base_frame:
    """The base class for all frames."""

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
        """

        # The label.
        label = wx.StaticText(parent, -1, text)

        # The font and label properties.
        label.SetMinSize((width, height))
        label.SetFont(self.gui.font_normal)

        # Add the label to the box.
        box.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)


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
        """

        # The control.
        field = control(parent, -1, text)

        # The font and control properties.
        field.SetMinSize((width, height))
        field.SetFont(self.gui.font_normal)
        field.SetEditable(editable)

        # Add the control to the box.
        box.Add(field, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

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
        label = wx.StaticText(self.parent, -1, text)

        # The font properties.
        label.SetFont(self.gui.font_title)

        # Pack the title, with spacing.
        box.AddSpacer(10)
        box.Add(label)
        box.AddSpacer(5)
