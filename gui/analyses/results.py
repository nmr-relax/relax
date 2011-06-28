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
from os import sep
import sys
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()

# relaxGUI module imports.
from gui.analyses.base import Base_frame
from gui.analyses.results_analysis import see_results
from gui.misc import add_border, gui_to_str, str_to_gui
from gui.paths import IMAGE_PATH



class Results_viewer(wx.Frame):
    """The base class for the noe frames."""

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
        self.button_open = wx.Button(self, -1, "Open")
        self.button_open.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.open_result_file, self.button_open)
        box_centre.Add(self.button_open, 0, wx.ALIGN_RIGHT, 5)

        # Bind some events.
        self.Bind(wx.EVT_SHOW, self.update_window)
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


    def add_model_free_results(self, box):
        """Function to pack rx results."""

        # Use a vertical packing of elements.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label.
        self.add_subsubtitle(sizer, "Model-free results")

        # Selection to open.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # Add results list box.
        self.gui.list_modelfree = self.add_list_box(sizer1, fn=self.gui.open_model_results_exe)

        # Add open button.
        button_modelfree = wx.Button(self.parent, -1, "Open")
        button_modelfree.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.gui.open_model_results_exe, button_modelfree)
        sizer1.Add(button_modelfree, 0, wx.LEFT, 5)

        # Add selection.
        sizer.Add(sizer1, 1, wx.ALL|wx.EXPAND, 0)

        # Add the element to the box.
        box.Add(sizer, 1, wx.ALL|wx.EXPAND, 0)


    def add_noe_results(self, box):
        """Function to pack noe results."""

        # Use a vertical packing of elements.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label.
        self.add_subsubtitle(sizer, "Steady-state NOE results")

        # Selection to open.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # Add results list box.
        self.gui.list_noe = self.add_list_box(sizer1, fn=self.gui.open_noe_results_exe)

        # Add open button.
        button_noe = wx.Button(self.parent, -1, "Open")
        button_noe.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.gui.open_noe_results_exe, button_noe)
        sizer1.Add(button_noe, 0, wx.LEFT, 5)

        # Add selection.
        sizer.Add(sizer1, 1, wx.ALL|wx.EXPAND, 0)

        # Add the element to the box.
        box.Add(sizer, 1, wx.ALL|wx.EXPAND, 0)


    def add_rx_results(self, box):
        """Function to pack rx results."""

        # Use a vertical packing of elements.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label.
        self.add_subsubtitle(sizer, "Relaxation results")

        # Selection to open.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # Add results list box.
        self.gui.list_rx = self.add_list_box(sizer1, fn=self.gui.open_rx_results_exe)

        # Add open button.
        button_rx = wx.Button(self.parent, -1, "Open")
        button_rx.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.gui.open_rx_results_exe, button_rx)
        sizer1.Add(button_rx, 0, wx.LEFT, 5)

        # Add selection.
        sizer.Add(sizer1, 1, wx.ALL|wx.EXPAND, 0)

        # Add the element to the box.
        box.Add(sizer, 1, wx.ALL|wx.EXPAND, 0)


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
        label.SetFont(self.gui.font_subtitle)

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


    def build_results_box(self, box):
        """Function to pack results frame.

        @param box: The horizontal box element to pack the elements into.
        @type box:  wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add the title.
        self.add_title(sizer, "Results")

        # Add Noe results.
        self.add_noe_results(sizer)

        # Add rx results.
        self.add_rx_results(sizer)

        # Add model-free results.
        self.add_model_free_results(sizer)

        # Add the sizer to the main box.
        box.Add(sizer, 1, wx.ALL|wx.EXPAND, 0)


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

        # Determine the analysis index.
        found = False
        for index in range(len(ds.relax_gui.analyses)):
            # Match.
            if gui_to_str(self.analysis_list.GetValue()) == ds.relax_gui.analyses[index].analysis_name:
                found = True
                break

        # No analysis chosen.
        if not found:
            return

        # Alias.
        data = ds.relax_gui.analyses[index]

        # Nothing to do.
        if not hasattr(data, 'results_list'):
            return

        # Update the list.
        for i in range(len(data.results_list)):
            self.list.Append(str_to_gui(data.results_list[i]))


    def open_result_file(self, event):
        """Open the results in the appropriate program.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The selected file.
        choice = gui_to_str(self.list.GetStringSelection())

        # No choice.
        if not choice:
            return

        # A special table.
        if choice == 'Table_of_Results':
            # The data.
            model_result = [ds.relax_gui.table_residue, ds.relax_gui.table_model, ds.relax_gui.table_s2, ds.relax_gui.table_rex, ds.relax_gui.table_te]

            # Open.
            see_results(choice, model_result)

        # Open the file.
        else:
            see_results(choice, None)


    def update_choices(self, event):
        """Update the list of analyses.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Clear the previous analyses.
        self.analysis_list.Clear()

        # The list of analyses.
        for i in range(len(ds.relax_gui.analyses)):
            self.analysis_list.Append(str_to_gui(ds.relax_gui.analyses[i].analysis_name))


    def update_window(self, event):
        """Update the window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Update the choices.
        self.update_choices(None)

        # Update the list.
        self.on_choice(None)
