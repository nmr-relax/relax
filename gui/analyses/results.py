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

        # Build and pack the main sizer box.
        main_box = self.build_results_box()
        self.parent.SetSizer(main_box)

        # Set the frame font size.
        self.parent.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))


    def add_model_free_results(self, box):
        """Function to pack rx results."""

        # Use a vertical packing of elements.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label.
        self.add_subsubtitle(sizer, "Model-free results")

        # Selection to open.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # Add results list box.
        self.gui.list_modelfree = wx.ListBox(self.parent, -1, choices=[])
        self.gui.list_modelfree.SetMinSize((800, 130))
        self.gui.Bind(wx.EVT_LISTBOX_DCLICK, self.gui.open_model_results_exe, self.gui.list_modelfree)
        sizer1.Add(self.gui.list_modelfree, 0, wx.EXPAND, 0)
        
        # Add open button.
        button_modelfree = wx.Button(self.parent, -1, "Open")
        button_modelfree.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.gui.open_model_results_exe, button_modelfree)
        sizer1.Add(button_modelfree, 0, wx.LEFT, 5)
        
        # Add selection.
        sizer.Add(sizer1, 0, wx.EXPAND, 0) 

        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def add_noe_results(self, box):
        """Function to pack noe results."""

        # Use a vertical packing of elements.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label.
        self.add_subsubtitle(sizer, "Steady-state NOE results")

        # Selection to open.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # Add results list box.
        self.gui.list_noe = wx.ListBox(self.parent, -1, choices=[])
        self.gui.list_noe.SetMinSize((800, 130))
        self.gui.Bind(wx.EVT_LISTBOX_DCLICK, self.gui.open_noe_results_exe, self.gui.list_noe)
        sizer1.Add(self.gui.list_noe, 0, wx.EXPAND, 0)
        
        # Add open button.
        button_noe = wx.Button(self.parent, -1, "Open")
        button_noe.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.gui.open_noe_results_exe, button_noe)
        sizer1.Add(button_noe, 0, wx.LEFT, 5)
        
        # Add selection.
        sizer.Add(sizer1, 0, wx.EXPAND, 0) 

        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def add_rx_results(self, box):
        """Function to pack rx results."""

        # Use a vertical packing of elements.
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Add a label.
        self.add_subsubtitle(sizer, "Relaxation results")

        # Selection to open.
        sizer1 = wx.BoxSizer(wx.HORIZONTAL)

        # Add results list box.
        self.gui.list_rx = wx.ListBox(self.parent, -1, choices=[])
        self.gui.list_rx.SetMinSize((800, 130))
        self.gui.Bind(wx.EVT_LISTBOX_DCLICK, self.gui.open_rx_results_exe, self.gui.list_rx)
        sizer1.Add(self.gui.list_rx, 0, wx.EXPAND, 0)
        
        # Add open button.
        button_rx = wx.Button(self.parent, -1, "Open")
        button_rx.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.gui.open_rx_results_exe, button_rx)
        sizer1.Add(button_rx, 0, wx.LEFT, 5)
        
        # Add selection.
        sizer.Add(sizer1, 0, wx.EXPAND, 0) 


        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def build_results_box(self):
        """Function to pack results frame."""

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the title.
        self.add_title(box, "Results")

        # Add Noe results.
        self.add_noe_results(box)

        # Add rx results.
        self.add_rx_results(box)

        # Add model-free results.
        self.add_model_free_results(box)

        return box

    def sync_results(self):
        """Function to synchronize results with relax data storage"""

        # load results from data store.
        self.results_noe = ds.relax_gui.results_noe
        self.results_rx = ds.relax_gui.results_rx
        self.results_modelfree = ds.relax_gui.results_model_free
