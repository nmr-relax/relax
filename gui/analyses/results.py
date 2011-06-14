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
from gui.misc import add_border
from gui.paths import IMAGE_PATH



class Results_summary(Base_frame):
    """The base class for the noe frames."""

    def __init__(self, gui, notebook):
        """Build the results frame.

        @param gui:                 The main GUI class.
        @type gui:                  gui.relax_gui.Main instance
        @param notebook:            The notebook to pack this frame into.
        @type notebook:             wx.Notebook instance
        """

        # Store the main class.
        self.gui = gui

        # Synchronize results.
        self.sync_results()

        # The parent GUI element for this class.
        self.parent = notebook

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.parent.SetSizer(box_main)

        # Build the central sizer, with borders.
        box_centre = add_border(box_main, border=self.border, packing=wx.HORIZONTAL)

        # Build and pack the main sizer box.
        self.build_results_box(box_centre)


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
        list = wx.ListBox(self.parent, -1, choices=[])

        # Set the properties.
        list.SetMinSize((400, 130))

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


    def sync_results(self):
        """Function to synchronize results with relax data storage"""

        # load results from data store.
        self.results_noe = ds.relax_gui.results_noe
        self.results_rx = ds.relax_gui.results_rx
        self.results_modelfree = ds.relax_gui.results_model_free
