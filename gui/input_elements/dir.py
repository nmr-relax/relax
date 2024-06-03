###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# Module docstring.
"""Module containing a set of special GUI elements to be used in the relax wizards."""

# Python module imports.
import wx

# relax module imports.
import dep_check
from graphics import fetch_icon
from gui.filedialog import RelaxDirDialog
from gui.fonts import font
from gui.string_conv import gui_to_str, str_to_gui
from lib.errors import RelaxError
from status import Status; status = Status()


class Selector_dir:
    """Wizard GUI element for selecting directories."""

    def __init__(self, name=None, default=None, parent=None, sizer=None, desc=None, message='File selection', style=wx.FD_DEFAULT_STYLE, tooltip=None, divider=None, padding=0, spacer=None, height_element=27, read_only=False):
        """Build the file selection element.

        @keyword name:              The name of the element to use in titles, etc.
        @type name:                 str
        @keyword default:           The default value of the element.
        @type default:              str
        @keyword parent:            The wizard GUI element.
        @type parent:               wx.Panel instance
        @keyword sizer:             The sizer to put the input field into.
        @type sizer:                wx.Sizer instance
        @keyword desc:              The text description.
        @type desc:                 str
        @keyword message:           The file selector prompt string.
        @type message:              String
        @keyword style:             The dialog style.  To open a single file, set to wx.FD_OPEN.  To open multiple files, set to wx.FD_OPEN|wx.FD_MULTIPLE.  To save a single file, set to wx.FD_SAVE.  To save multiple files, set to wx.FD_SAVE|wx.FD_MULTIPLE.
        @type style:                long
        @keyword tooltip:           The tooltip which appears on hovering over all the GUI elements.
        @type tooltip:              str
        @keyword divider:           The position of the divider.
        @type divider:              int
        @keyword padding:           Spacing to the left and right of the widgets.
        @type padding:              int
        @keyword spacer:            The amount of spacing to add below the field in pixels.  If None, a stretchable spacer will be used.
        @type spacer:               None or int
        @keyword height_element:    The height in pixels of the GUI element.
        @type height_element:       int
        @keyword read_only:         A flag which if True means that the text of the element cannot be edited.
        @type read_only:            bool
        """

        # Store the args.
        self.name = name

        # Argument translation.
        if default == None:
            default = wx.EmptyString

        # Init.
        sub_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Left padding.
        sub_sizer.AddSpacer(padding)

        # The description.
        text = wx.StaticText(parent, -1, desc, style=wx.ALIGN_LEFT)
        text.SetFont(font.normal)
        sub_sizer.Add(text, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

        # The divider.
        if not divider:
            raise RelaxError("The divider position has not been supplied.")

        # Spacing.
        dc = wx.ScreenDC()
        dc.SetFont(font.normal)
        x, y = dc.GetTextExtent(desc)
        if dep_check.wx_classic:
            sub_sizer.AddSpacer((divider - x, 0))
        else:
            sub_sizer.AddSpacer(int(divider - x))

        # The input field.
        self._field = wx.TextCtrl(parent, -1, default)
        self._field.SetMinSize((-1, height_element))
        self._field.SetFont(font.normal)
        sub_sizer.Add(self._field, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # The directory selection object.
        obj = RelaxDirDialog(parent, field=self._field, message=message, defaultPath=default, style=style)

        # A little spacing.
        sub_sizer.AddSpacer(5)

        # The file selection button.
        button = wx.BitmapButton(parent, -1, wx.Bitmap(fetch_icon('oxygen.actions.document-open-folder'), wx.BITMAP_TYPE_ANY))
        button.SetMinSize((-1, height_element))
        button.SetToolTip(wx.ToolTip("Select the directory."))
        sub_sizer.Add(button, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)
        parent.Bind(wx.EVT_BUTTON, obj.select_event, button)

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
            text.SetToolTip(wx.ToolTip(tooltip))
            self._field.SetToolTip(wx.ToolTip(tooltip))


    def Clear(self):
        """Special method for clearing or resetting the GUI element."""

        # Clear the value from the TextCtrl.
        self._field.Clear()


    def GetValue(self):
        """Special method for returning the value of the GUI element.

        @return:    The string value.
        @rtype:     list of str
        """

        # Convert and return the value from a TextCtrl.
        return gui_to_str(self._field.GetValue())


    def SetValue(self, value):
        """Special method for setting the value of the GUI element.

        @param value:   The value to set.
        @type value:    str
        """

        # Convert and set the value for a TextCtrl.
        self._field.SetValue(str_to_gui(value))
