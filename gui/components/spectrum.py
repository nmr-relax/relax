###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
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
"""Module containing the classes for GUI components involving spectral data."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from status import Status; status = Status()
from generic_fns.spectrum import replicated_flags, replicated_ids

# relax GUI module imports.
from gui.fonts import font
from gui.misc import add_border, float_to_gui, str_to_gui
from gui import paths


class Spectra_list:
    """The GUI element for listing loaded spectral data."""

    def __init__(self, gui=None, parent=None, box=None, id=None, fn_add=None, buttons=True):
        """Build the spectral list GUI element.

        @keyword gui:       The main GUI object.
        @type gui:          wx.Frame instance
        @keyword parent:    The parent GUI element that this is to be attached to (the panel object).
        @type parent:       wx object
        @keyword data:      The data storage container.
        @type data:         class instance
        @keyword box:       The vertical box sizer to pack this GUI component into.
        @type box:          wx.BoxSizer instance
        @keyword id:        A unique identification string.  This is used to register the update method with the GUI user function observer object.
        @type id:           str
        @keyword fn_add:    The function to execute when clicking on the 'Add' button.
        @type fn_add:       func
        @keyword buttons:   A flag which if True will display the buttons at the top.
        @type buttons:      bool
        """

        # Store the arguments.
        self.gui = gui
        self.parent = parent
        self.fn_add = fn_add

        # GUI variables.
        self.spacing = 5
        self.border = 5
        self.height_buttons = 40

        # First create a panel (to allow for tooltips on the buttons).
        self.panel = wx.Panel(self.parent)
        box.Add(self.panel, 0, wx.ALL|wx.EXPAND, 0)

        # Add a sizer to the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(panel_sizer)

        # A static box to hold all the widgets, and its sizer.
        stat_box = wx.StaticBox(self.panel, -1, "Spectra list")
        stat_box.SetFont(font.subtitle)
        sub_sizer = wx.StaticBoxSizer(stat_box, wx.VERTICAL)

        # Add the sizer to the static box and the static box to the main box.
        panel_sizer.Add(sub_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Add a border.
        box_centre = add_border(sub_sizer, border=self.border)

        # Add buttons.
        if buttons:
            self.add_buttons(box_centre)

        # Initialise the element.
        box_centre.AddSpacer(self.spacing)
        self.init_element(box_centre)

        # Build the element.
        self.build_element()

        # Initialise observer name.
        self.name = 'spectra list: %s' % id

        # Register the element for updating when a user function completes.
        status.observers.gui_uf.register(self.name, self.build_element)


    def add_buttons(self, sizer):
        """Add the buttons for peak list manipulation.

        @param box:     The sizer element to pack the buttons into.
        @type box:      wx.BoxSizer instance
        """

        # Button Sizer
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Add button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self.panel, -1, None, " Add")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.add, wx.BITMAP_TYPE_ANY))
        button.SetSize((80, self.height_buttons))
        button_sizer.Add(button, 0, 0, 0)
        self.gui.Bind(wx.EVT_BUTTON, self.fn_add, button)
        button.SetToolTipString("Read a spectral data file.")


    def build_element(self):
        """Build the spectra listing GUI element."""

        # First freeze the element, so that the GUI element doesn't update until the end.
        self.element.Freeze()

        # Initialise the column index for the data.
        index = 1

        # Delete the rows and columns.
        self.element.DeleteAllItems()
        for i in range(1, self.element.GetColumnCount()):
            self.element.DeleteColumn(i)

        # Expand the number of rows to match the number of spectrum IDs, and add the IDs.
        n = 0
        if hasattr(cdp, 'spectrum_ids'):
            # The number of IDs.
            n = len(cdp.spectrum_ids)

            # Set the IDs.
            for i in range(n):
                self.element.InsertStringItem(i, str_to_gui(cdp.spectrum_ids[i]))

        # The NOE spectrum type.
        if self.noe_spectrum_type(index):
            index += 1

        # The relaxation times.
        if self.relax_times(index):
            index += 1

        # The replicated spectra.
        if self.replicates(index):
            index += 1

        # Size the columns.
        self.size_cols()

        # Post a size event to get the scroll panel to update correctly.
        event = wx.PyCommandEvent(wx.EVT_SIZE.typeId, self.parent.GetId())
        wx.PostEvent(self.parent.GetEventHandler(), event)

        # Set the minimum height.
        height = self.height_char * (n + 1) + 50
        self.element.SetMinSize((-1, height))
        self.element.Layout()

        # Unfreeze.
        self.element.Thaw()


    def delete(self):
        """Unregister the class."""

        # Unregister the class.
        status.observers.gui_uf.unregister(self.name)


    def init_element(self, sizer):
        """Initialise the GUI element for the spectra listing.

        @param box:     The sizer element to pack the element into.
        @type box:      wx.BoxSizer instance
        """

        # List of peak list file names and relaxation time.
        self.element = wx.ListCtrl(self.panel, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Initialise to a single column.
        self.element.InsertColumn(0, str_to_gui("Spectrum ID string"))

        # Properties.
        self.element.SetFont(font.normal)

        # Store the base heights.
        self.height_char = self.element.GetCharHeight()

        # Bind some events.
        self.element.Bind(wx.EVT_SIZE, self.resize)

        # Add list to sizer.
        sizer.Add(self.element, 0, wx.ALL|wx.EXPAND, 0)


    def resize(self, event):
        """Catch the resize to allow the element to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the column sizes.
        self.size_cols()

        # Continue with the normal resizing.
        event.Skip()


    def noe_spectrum_type(self, index):
        """Add the NOE spectral type info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if a spectrum type exists, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'spectrum_type') or not len(cdp.spectrum_type):
            return False

        # Append a column.
        self.element.InsertColumn(index, str_to_gui("NOE spectrum type"))

        # Translation table.
        table = {
            'sat': 'Saturated',
            'ref': 'Reference'
        }

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.spectrum_type.keys():
                continue

            # Set the value.
            self.element.SetStringItem(i, index, str_to_gui(table[cdp.spectrum_type[cdp.spectrum_ids[i]]]))

        # Successful.
        return True


    def relax_times(self, index):
        """Add the relaxation delay time info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if relaxation times exist, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'relax_times') or not len(cdp.relax_times):
            return False

        # Append a column.
        self.element.InsertColumn(index, str_to_gui("Delay times"))

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.relax_times.keys():
                continue

            # Set the value.
            self.element.SetStringItem(i, index, float_to_gui(cdp.relax_times[cdp.spectrum_ids[i]]))

        # Successful.
        return True


    def replicates(self, index):
        """Add the replicated spectra info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if relaxation times exist, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'replicates') or not len(cdp.replicates):
            return False

        # Replicated spectra.
        repl = replicated_flags()

        # Append a column.
        self.element.InsertColumn(index, str_to_gui("Replicate IDs"))

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No replicates.
            if not repl[cdp.spectrum_ids[i]]:
                continue

            # The replicated spectra.
            id_list = replicated_ids(cdp.spectrum_ids[i])

            # Convert to a string.
            text = ''
            for j in range(len(id_list)):
                # Add the id.
                text = "%s%s" % (text, id_list[j])

                # Separator.
                if j < len(id_list)-1:
                    text = "%s, " % text

            # Set the value.
            self.element.SetStringItem(i, index, str_to_gui(text))

        # Successful.
        return True


    def size_cols(self):
        """Set the column sizes."""

        # The element size.
        x, y = self.element.GetSize()

        # Number of columns.
        n = self.element.GetColumnCount()

        # Set to equal sizes.
        width = int(x / n)

        # Set the column sizes.
        for i in range(n):
            self.element.SetColumnWidth(i, width)
