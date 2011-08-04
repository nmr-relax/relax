###############################################################################
#                                                                             #
# Copyright (C) 2010 Michael Bieri                                            #
# Copyright (C) 2011 Edward d'Auvergne                                        #
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
"""Module containing the base class for the results frame."""

# Python module imports.
from string import upper
import wx
from wx.lib import buttons

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()

# relax GUI module imports.
from gui.analyses.results_analysis import see_results
from gui.fonts import font
from gui.icons import relax_icons
from gui.misc import add_border, gui_to_str, open_file, str_to_gui
from gui.paths import icon_22x22


class Results_viewer(wx.Frame):
    """The results viewer frame."""

    # Some class variables.
    border = 10
    size = (800, 400)

    def __init__(self, gui):
        """Build the results frame.

        @param gui:                 The main GUI class.
        @type gui:                  gui.relax_gui.Main instance
        """

        # Store the main class.
        self.gui = gui

        # Initialise the base frame.
        wx.Frame.__init__(self, parent=gui, style=wx.DEFAULT_FRAME_STYLE)

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Set the window title, size, etc.
        self.SetTitle("Results viewer")
        self.SetSize(self.size)

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(box_main)

        # Build the central sizer, with borders.
        box_centre = add_border(box_main, border=self.border, packing=wx.VERTICAL)

        # Build the analysis selector.
        self.build_analysis_sel(box_centre)

        # Spacer.
        box_centre.AddSpacer(self.border)

        # Add the list box.
        self.list = self.add_list_box(box_centre, fn=None)

        # Spacer.
        box_centre.AddSpacer(self.border)

        # Add the open button.
        self.button_open = buttons.ThemedGenBitmapTextButton(self, -1, None, " Open")
        self.button_open.SetBitmapLabel(wx.Bitmap(icon_22x22.document_open, wx.BITMAP_TYPE_ANY))
        self.button_open.SetFont(font.normal)
        self.button_open.SetMinSize((103, 33))
        self.gui.Bind(wx.EVT_BUTTON, self.open_result_file, self.button_open)
        box_centre.Add(self.button_open, 0, wx.ALIGN_RIGHT|wx.ADJUST_MINSIZE, 5)

        # Bind some events.
        self.Bind(wx.EVT_LEFT_DOWN, self.update_choices, self.analysis_list)
        self.Bind(wx.EVT_COMBOBOX, self.on_choice, self.analysis_list)
        self.Bind(wx.EVT_CLOSE, self.handler_close)


    def add_list_box(self, box, fn=None):
        """Add a results list box.

        @param box:     The box sizer to pack the box into.
        @type box:      wx.BoxSizer instance
        @keyword fn:    The function to bind double click events to.
        @type fn:       method
        @return:        The list box element.
        @rtype:         wx.ListBox element
        """

        # Initialise the list box.
        list = wx.ListBox(self, -1, choices=[])

        # Bind events.
        self.gui.Bind(wx.EVT_LISTBOX_DCLICK, fn, list)

        # Add to the sizer.
        box.Add(list, 1, wx.ALL|wx.EXPAND, 0)

        # Return the list box.
        return list


    def build_analysis_sel(self, box):
        """Create the analysis selection element.

        @param box: The horizontal box element to pack the elements into.
        @type box:  wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The text.
        label = wx.StaticText(self, -1, "Analysis selection")

        # The font and label properties.
        label.SetFont(font.subtitle)

        # Add the label to the analysis box.
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add a spacer.
        sizer.AddSpacer(self.border)

        # A combo box.
        self.analysis_list = wx.ComboBox(self, -1, value='', style=wx.CB_DROPDOWN|wx.CB_READONLY, choices=[])
        self.analysis_list.SetMinSize((50, 27))
        sizer.Add(self.analysis_list, 1, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add the analysis sizer to the main sizer.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Hide()


    def on_choice(self, event):
        """Update the list of results on choosing an analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the list.
        self.list.Clear()

        # Get the page corresponding to the choice.
        page = self.gui.analysis.get_page_from_name(gui_to_str(self.analysis_list.GetValue()))

        # Nothing to do.
        if not hasattr(cdp, 'result_files'):
            return

        # Update the list.
        for i in range(len(cdp.result_files)):
            # The text to display.
            text = "%s%s file:  %s" % (upper(cdp.result_files[i][0][0]), cdp.result_files[i][0][1:], cdp.result_files[i][1])

            # Add the text with the Python data.
            self.list.Append(str_to_gui(text), clientData=cdp.result_files[i])


    def open_result_file(self, event):
        """Open the results in the appropriate program.

        @param event:   The wx event.
        @type event:    wx event
        """

        # No choice.
        if self.list.GetSelection() == wx.NOT_FOUND:
            return

        # Get the data.
        data = self.list.GetClientData(self.list.GetSelection())

        # Grace files.
        if data[0] == 'grace':
            print "grace"

        # A special table.
        elif data[0] == 'Table_of_Results':
            # The data.
            model_result = [ds.relax_gui.table_residue, ds.relax_gui.table_model, ds.relax_gui.table_s2, ds.relax_gui.table_rex, ds.relax_gui.table_te]

            # Open.
            see_results(choice, model_result)

        # Open all other files in which ever editor the platform decides on.
        else:
            open_file(data[1])



    def update_choices(self, event):
        """Update the list of analyses.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous analyses.
        self.analysis_list.Clear()

        # The list of analyses.
        for data in self.gui.analysis.analysis_data_loop():
            self.analysis_list.Append(str_to_gui(data.analysis_name))

        # Set the name to the current analysis.
        self.analysis_list.SetValue(str_to_gui(self.gui.analysis.current_analysis_name()))


    def update_window(self, event=None):
        """Update the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Update the choices.
        self.update_choices(None)

        # Update the list.
        self.on_choice(None)
