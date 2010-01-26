###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010 Edward d'Auvergne                                        #
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
"""Main module for the relax graphical user interface."""

# Python module imports.
from os import getcwd, sep
import wx

# relax GUI module imports.
from gui_bieri.analyses.relax_control import start_modelfree
from gui_bieri.analyses.results_analysis import model_free_results, see_results
from gui_bieri.analyses.select_model_calc import Select_tensor
from gui_bieri.derived_wx_classes import StructureTextCtrl
from gui_bieri.filedialog import opendir, openfile
from gui_bieri.message import missing_data
from gui_bieri.paths import IMAGE_PATH


class Auto_model_free:
    def __init__(self, gui):
        """Build the automatic model-free protocol GUI element.

        @param gui: The main GUI class.
        @type gui:  gui_bieri.relax_gui.Main instance
        """

        # Store the main class.
        self.gui = gui

        # Model-free variables.
        self.model_source = getcwd()
        self.model_save = getcwd()
        self.selection = "AIC"
        self.models = ["m0", "m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8", "m9"]
        self.nmrfreq1 = 600
        self.nmrfreq2 = 800
        self.nmrfreq3 = 900
        self.paramfiles1 = ["", "", ""]
        self.paramfiles2 = ["", "", ""]
        self.paramfiles3 = ["", "", ""]
        self.results_dir_model = getcwd()

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        main_box = self.build_main_box()
        self.gui.modelfree.SetSizer(main_box)

        # Set the frame font size.
        self.gui.modelfree.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))


    def add_execute_relax(self, box):
        """Create and add the relax execution GUI element to the given box.

        @param box:     The box element to pack the relax execution GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # The elements.
        self.label_5_copy_1_copy_3 = wx.StaticText(self.gui.modelfree, -1, "Execute relax        ", style=wx.ALIGN_RIGHT)
        self.relax_start_modelfree = wx.BitmapButton(self.gui.modelfree, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))

        # Properties.
        self.label_5_copy_1_copy_3.SetMinSize((118, 17))
        self.label_5_copy_1_copy_3.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.relax_start_modelfree.SetName('hello')
        self.relax_start_modelfree.SetSize(self.relax_start_modelfree.GetBestSize())

        # Layout.
        exec_relax_copy_1_copy_3 = wx.BoxSizer(wx.HORIZONTAL)
        exec_relax_copy_1_copy_3.Add(self.label_5_copy_1_copy_3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        exec_relax_copy_1_copy_3.Add(self.relax_start_modelfree, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)

        # Bind the events.
        self.gui.Bind(wx.EVT_BUTTON, self.exec_model_free, self.relax_start_modelfree)

        # Add the element to the box.
        box.Add(exec_relax_copy_1_copy_3, 1, wx.ALIGN_RIGHT, 0)


    def add_frame_title(self, box):
        """Create and add the frame title to the given box.

        @param box:     The box element to pack the frame title into.
        @type box:      wx.BoxSizer instance
        """

        # The title.
        label = wx.StaticText(self.gui.modelfree, -1, "Set-up for Model-free analysis:")

        # The font properties.
        label.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))

        # Pack the title.
        box.Add(label, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)


    def add_mf_models(self, box):
        """Create and add the model-free model picking GUI element to the given box.

        @param box:     The box element to pack the model-free model picking GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # The elements.
        self.label_9 = wx.StaticText(self.gui.modelfree, -1, "Select Model-free models (default = all):")
        self.m0 = wx.ToggleButton(self.gui.modelfree, -1, "m0")
        self.m1 = wx.ToggleButton(self.gui.modelfree, -1, "m1")
        self.m2 = wx.ToggleButton(self.gui.modelfree, -1, "m2")
        self.m3 = wx.ToggleButton(self.gui.modelfree, -1, "m3")
        self.m4 = wx.ToggleButton(self.gui.modelfree, -1, "m4")
        self.m5 = wx.ToggleButton(self.gui.modelfree, -1, "m5")
        self.m6 = wx.ToggleButton(self.gui.modelfree, -1, "m6")
        self.m7 = wx.ToggleButton(self.gui.modelfree, -1, "m7")
        self.m8 = wx.ToggleButton(self.gui.modelfree, -1, "m8")
        self.m9 = wx.ToggleButton(self.gui.modelfree, -1, "m9")

        # Properties.
        self.m0.SetMinSize((70, 25))
        self.m0.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m0.SetToolTipString("{}")
        self.m0.SetValue(1)
        self.m1.SetMinSize((70, 25))
        self.m1.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m1.SetToolTipString("{S2}")
        self.m1.SetValue(1)
        self.m2.SetMinSize((70, 25))
        self.m2.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m2.SetToolTipString("{S2, te}")
        self.m2.SetValue(1)
        self.m3.SetMinSize((70, 25))
        self.m3.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m3.SetToolTipString("{S2, Rex}")
        self.m3.SetValue(1)
        self.m4.SetMinSize((70, 25))
        self.m4.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m4.SetToolTipString("{S2, te, Rex}")
        self.m4.SetValue(1)
        self.m5.SetMinSize((70, 25))
        self.m5.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m5.SetToolTipString("{S2, S2f, ts}")
        self.m5.SetValue(1)
        self.m6.SetMinSize((70, 25))
        self.m6.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m6.SetToolTipString("{S2, tf, S2f, ts}")
        self.m6.SetValue(1)
        self.m7.SetMinSize((70, 25))
        self.m7.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m7.SetToolTipString("{S2, S2f, ts, Rex}")
        self.m7.SetValue(1)
        self.m8.SetMinSize((70, 25))
        self.m8.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m8.SetToolTipString("{S2, tf, S2f, ts, Rex}")
        self.m8.SetValue(1)
        self.m9.SetMinSize((70, 25))
        self.m9.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        self.m9.SetToolTipString("{Rex}")
        self.m9.SetValue(1)

        # Lay out the model buttons into the sizer.
        sizer_20 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_20.Add(self.m0, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m4, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m5, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m6, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m7, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m8, 0, wx.ADJUST_MINSIZE, 0)
        sizer_20.Add(self.m9, 0, wx.ADJUST_MINSIZE, 0)

        # Add the title and box of buttons.
        box.Add(self.label_9, 0, wx.TOP|wx.ADJUST_MINSIZE, 10)
        box.Add(sizer_20, 1, wx.EXPAND, 0)


    def add_modsel_method(self, box):
        """Create and add the model selection choice GUI element to the given box.

        @param box:     The box element to pack the model selection choice GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # The elements.
        self.label_10 = wx.StaticText(self.gui.modelfree, -1, "Select Model-free selection mode:      ")
        self.aic = wx.RadioButton(self.gui.modelfree, -1, "AIC")
        self.bic = wx.RadioButton(self.gui.modelfree, -1, "BIC")

        # Properties.
        self.label_10.SetMinSize((240, 17))
        self.label_10.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.aic.SetMinSize((60, 22))

        # Layout.
        sizer_21 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_21.Add(self.label_10, 0, wx.TOP|wx.ADJUST_MINSIZE, 1)
        sizer_21.Add(self.aic, 0, wx.ADJUST_MINSIZE, 0)
        sizer_21.Add(self.bic, 0, wx.ADJUST_MINSIZE, 0)

        # Bind the events.
        self.gui.Bind(wx.EVT_RADIOBUTTON, self.sel_aic, self.aic)
        self.gui.Bind(wx.EVT_RADIOBUTTON, self.sel_bic, self.bic)

        # Add the sizer to the box.
        box.Add(sizer_21, 1, wx.TOP|wx.EXPAND, 5)


    def add_pdb_selection(self, box):
        """Create and add the PDB file selection GUI element to the given box.

        @param box:     The box element to pack the PDB file selection GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # The elements.
        self.structure_file_copy_copy_1_copy = wx.StaticText(self.gui.modelfree, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        self.structure_r21_copy_1_copy = StructureTextCtrl(self.gui.modelfree, -1, self.gui.structure_file_pdb_msg)
        self.structure_r21_copy_1_copy.SetEditable(False)
        self.chan_struc_r21_copy_1_copy = wx.Button(self.gui.modelfree, -1, "Change")

        # Properties.
        self.structure_file_copy_copy_1_copy.SetMinSize((240, 17))
        self.structure_file_copy_copy_1_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.structure_r21_copy_1_copy.SetMinSize((350, 27))
        self.chan_struc_r21_copy_1_copy.SetMinSize((103, 27))

        # Layout.
        results_dir_copy_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)

        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.structure_file_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.structure_r21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_copy_copy_1_copy.Add(self.chan_struc_r21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)

        # Bind the events.
        self.gui.Bind(wx.EVT_BUTTON, self.structure_r21_copy_1_copy.open_file, self.chan_struc_r21_copy_1_copy)

        # Add the element to the box.
        box.Add(results_dir_copy_copy_copy_copy_copy_1_copy, 1, wx.EXPAND, 0)


    def add_relax_data_input(self, box):
        """Create and add the relaxation data input GUI element to the given box.

        @param box:     The box element to pack the relax data input GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Create the panel.
        panel_4_copy_1 = wx.Panel(self.gui.modelfree, -1)
        panel_4_copy = wx.Panel(self.gui.modelfree, -1)
        panel_4 = wx.Panel(self.gui.modelfree, -1)

        # The 1st panel contents.
        label_7 = wx.StaticText(panel_4, -1, "NMR freq 1:")
        self.modelfreefreq1 = wx.TextCtrl(panel_4, -1, "")
        label_8 = wx.StaticText(panel_4, -1, "NOE")
        self.m_noe_1 = wx.TextCtrl(panel_4, -1, "")
        model_noe_1 = wx.Button(panel_4, -1, "+")
        label_8_copy = wx.StaticText(panel_4, -1, "R1")
        self.m_r1_1 = wx.TextCtrl(panel_4, -1, "")
        model_r1_1 = wx.Button(panel_4, -1, "+")
        label_8_copy_copy = wx.StaticText(panel_4, -1, "R2")
        self.m_r2_1 = wx.TextCtrl(panel_4, -1, "")
        model_r2_1 = wx.Button(panel_4, -1, "+")

        # The 2nd panel contents.
        label_7_copy = wx.StaticText(panel_4_copy, -1, "NMR freq 2:")
        self.modelfreefreq2 = wx.TextCtrl(panel_4_copy, -1, "")
        label_8_copy_1 = wx.StaticText(panel_4_copy, -1, "NOE")
        self.m_noe_2 = wx.TextCtrl(panel_4_copy, -1, "")
        model_noe_2 = wx.Button(panel_4_copy, -1, "+")
        label_8_copy_copy_1 = wx.StaticText(panel_4_copy, -1, "R1")
        self.m_r1_2 = wx.TextCtrl(panel_4_copy, -1, "")
        model_r1_2 = wx.Button(panel_4_copy, -1, "+")
        label_8_copy_copy_copy = wx.StaticText(panel_4_copy, -1, "R2")
        self.m_r2_2 = wx.TextCtrl(panel_4_copy, -1, "")
        model_r2_2 = wx.Button(panel_4_copy, -1, "+")

        # The 3rd panel contents.
        label_7_copy_copy = wx.StaticText(panel_4_copy_1, -1, "NMR freq 3:")
        self.modelfreefreq3 = wx.TextCtrl(panel_4_copy_1, -1, "")
        label_8_copy_1_copy = wx.StaticText(panel_4_copy_1, -1, "NOE")
        self.m_noe_3 = wx.TextCtrl(panel_4_copy_1, -1, "")
        model_noe_3 = wx.Button(panel_4_copy_1, -1, "+")
        label_8_copy_copy_1_copy = wx.StaticText(panel_4_copy_1, -1, "R1")
        self.m_r1_3 = wx.TextCtrl(panel_4_copy_1, -1, "")
        model_r1_3 = wx.Button(panel_4_copy_1, -1, "+")
        label_8_copy_copy_copy_copy = wx.StaticText(panel_4_copy_1, -1, "R2")
        self.m_r2_3 = wx.TextCtrl(panel_4_copy_1, -1, "")
        model_r2_3 = wx.Button(panel_4_copy_1, -1, "+")

        # Properties.
        label_7.SetMinSize((80, 17))
        self.modelfreefreq1.SetMinSize((80, 20))
        label_8.SetMinSize((80, 17))
        self.m_noe_1.SetMinSize((120, 20))
        model_noe_1.SetMinSize((20, 20))
        model_noe_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_8_copy.SetMinSize((80, 17))
        self.m_r1_1.SetMinSize((120, 20))
        model_r1_1.SetMinSize((20, 20))
        model_r1_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_8_copy_copy.SetMinSize((80, 17))
        self.m_r2_1.SetMinSize((120, 20))
        model_r2_1.SetMinSize((20, 20))
        model_r2_1.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_7_copy.SetMinSize((80, 17))
        self.modelfreefreq2.SetMinSize((80, 20))
        label_8_copy_1.SetMinSize((80, 17))
        self.m_noe_2.SetMinSize((120, 20))
        model_noe_2.SetMinSize((20, 20))
        model_noe_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_8_copy_copy_1.SetMinSize((80, 17))
        self.m_r1_2.SetMinSize((120, 20))
        model_r1_2.SetMinSize((20, 20))
        model_r1_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_8_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_2.SetMinSize((120, 20))
        model_r2_2.SetMinSize((20, 20))
        model_r2_2.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_7_copy_copy.SetMinSize((80, 17))
        self.modelfreefreq3.SetMinSize((80, 20))
        label_8_copy_1_copy.SetMinSize((80, 17))
        self.m_noe_3.SetMinSize((120, 20))
        model_noe_3.SetMinSize((20, 20))
        model_noe_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_8_copy_copy_1_copy.SetMinSize((80, 17))
        self.m_r1_3.SetMinSize((120, 20))
        model_r1_3.SetMinSize((20, 20))
        model_r1_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))
        label_8_copy_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_3.SetMinSize((120, 20))
        model_r2_3.SetMinSize((20, 20))
        model_r2_3.SetFont(wx.Font(6, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))

        # The box layout.
        sizer_16 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17 = wx.BoxSizer(wx.VERTICAL)
        sizer_18 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17_copy_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_17_copy = wx.BoxSizer(wx.VERTICAL)
        sizer_19_copy_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_18_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_19_copy = wx.BoxSizer(wx.HORIZONTAL)
        panel_4_copy_1.SetSizer(sizer_17_copy_copy)

        # Setup and pack the elements.
        panel_4.SetMinSize((230, 85))
        panel_4.SetBackgroundColour(wx.Colour(192, 192, 192))
        panel_4_copy.SetMinSize((230, 85))
        panel_4_copy.SetBackgroundColour(wx.Colour(176, 176, 176))
        panel_4_copy_1.SetMinSize((230, 85))
        panel_4_copy_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        sizer_18.Add(label_7, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18.Add(self.modelfreefreq1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_18, 0, 0, 0)
        sizer_19.Add(label_8, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19.Add(self.m_noe_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19.Add(model_noe_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy.Add(label_8_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy.Add(self.m_r1_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy.Add(model_r1_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy.Add(label_8_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy.Add(self.m_r2_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy.Add(model_r2_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17.Add(sizer_19_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        panel_4.SetSizer(sizer_17)
        sizer_16.Add(panel_4, 0, 0, 0)
        sizer_18_copy.Add(label_7_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18_copy.Add(self.modelfreefreq2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_18_copy, 0, 0, 0)
        sizer_19_copy_1.Add(label_8_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1.Add(self.m_noe_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1.Add(model_noe_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_1.Add(label_8_copy_copy_1, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1.Add(self.m_r1_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1.Add(model_r1_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_copy_1, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_copy.Add(label_8_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy.Add(self.m_r2_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy.Add(model_r2_2, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy.Add(sizer_19_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        panel_4_copy.SetSizer(sizer_17_copy)
        sizer_16.Add(panel_4_copy, 0, 0, 0)
        sizer_18_copy_copy.Add(label_7_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_18_copy_copy.Add(self.modelfreefreq3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_18_copy_copy, 0, 0, 0)
        sizer_19_copy_1_copy.Add(label_8_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1_copy.Add(self.m_noe_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_1_copy.Add(model_noe_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_1_copy.Add(label_8_copy_copy_1_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1_copy.Add(self.m_r1_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_1_copy.Add(model_r1_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_19_copy_copy_copy_copy.Add(label_8_copy_copy_copy_copy, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy_copy.Add(self.m_r2_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_19_copy_copy_copy_copy.Add(model_r2_3, 0, wx.ADJUST_MINSIZE, 0)
        sizer_17_copy_copy.Add(sizer_19_copy_copy_copy_copy, 0, wx.EXPAND|wx.SHAPED, 0)
        sizer_16.Add(panel_4_copy_1, 0, 0, 0)

        # Button actions.
        self.gui.Bind(wx.EVT_BUTTON, self.model_noe1, model_noe_1)
        self.gui.Bind(wx.EVT_BUTTON, self.model_r11,  model_r1_1)
        self.gui.Bind(wx.EVT_BUTTON, self.model_r21,  model_r2_1)
        self.gui.Bind(wx.EVT_BUTTON, self.model_noe2, model_noe_2)
        self.gui.Bind(wx.EVT_BUTTON, self.model_r12,  model_r1_2)
        self.gui.Bind(wx.EVT_BUTTON, self.model_r22,  model_r2_2)
        self.gui.Bind(wx.EVT_BUTTON, self.model_noe3, model_noe_3)
        self.gui.Bind(wx.EVT_BUTTON, self.model_r13,  model_r1_3)
        self.gui.Bind(wx.EVT_BUTTON, self.model_r23,  model_r2_3)

        # Add the sizer to the given box.
        box.Add(sizer_16, 0, 0, 0)


    def add_results_dir(self, box):
        """Create and add the results directory GUI element to the given box.

        @param box:     The box element to pack the results directory GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # The elements.
        self.label_2_copy_copy_3_copy_copy_copy_copy_2 = wx.StaticText(self.gui.modelfree, -1, "Results directory", style=wx.ALIGN_RIGHT)
        self.resultsdir_r21_copy_2 = wx.TextCtrl(self.gui.modelfree, -1, self.results_dir_model)
        self.results_directory_r21_copy_2 = wx.Button(self.gui.modelfree, -1, "Change")

        # Properties.
        results_dir_copy_copy_copy_1_copy_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.resultsdir_r21_copy_2.SetMinSize((350, 27))
        self.results_directory_r21_copy_2.SetMinSize((103, 27))
        self.label_2_copy_copy_3_copy_copy_copy_copy_2.SetMinSize((240, 17))
        self.label_2_copy_copy_3_copy_copy_copy_copy_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))

        # Layout.
        results_dir_copy_copy_copy_1_copy_2.Add(self.label_2_copy_copy_3_copy_copy_copy_copy_2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.resultsdir_r21_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        results_dir_copy_copy_copy_1_copy_2.Add(self.results_directory_r21_copy_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)

        # Bind the events.
        self.gui.Bind(wx.EVT_BUTTON, self.resdir_modelfree, self.results_directory_r21_copy_2)


        # Add the element to the box.
        box.Add(results_dir_copy_copy_copy_1_copy_2, 1, wx.EXPAND, 0)


    def add_unresolved_spins(self, box):
        """Create and add the unresolved spins GUI element to the given box.

        @param box:     The box element to pack the unresolved spins GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # The elements.
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy = wx.StaticText(self.gui.modelfree, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        self.unresolved_r21_copy_1_copy = wx.TextCtrl(self.gui.modelfree, -1, "")

        # Properties.
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy.SetMinSize((240, 17))
        self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        self.unresolved_r21_copy_1_copy.SetMinSize((350, 27))

        # Layout.
        nmr_freq_copy_copy_copy_copy_copy_1_copy = wx.BoxSizer(wx.HORIZONTAL)
        nmr_freq_copy_copy_copy_copy_copy_1_copy.Add(self.label_2_copy_copy_copy_2_copy_copy_copy_copy_1_copy, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        nmr_freq_copy_copy_copy_copy_copy_1_copy.Add(self.unresolved_r21_copy_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Bind the events.

        # Add the element to the box.
        box.Add(nmr_freq_copy_copy_copy_copy_copy_1_copy, 0, wx.EXPAND|wx.SHAPED, 0)


    def build_main_box(self):
        """Construct the highest level box to pack into the automatic model-free analysis frame.

        @return:    The main box element containing all model-free GUI elements to pack directly into the automatic model-free analysis frame.
        @rtype:     wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        box = wx.BoxSizer(wx.HORIZONTAL)

        # Add the model-free bitmap picture.
        bitmap = wx.StaticBitmap(self.gui.modelfree, -1, wx.Bitmap(IMAGE_PATH+'modelfree.png', wx.BITMAP_TYPE_ANY))
        box.Add(bitmap, 0, wx.ADJUST_MINSIZE, 0)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 0, 0, 0)

        # Return the box.
        return box


    def build_right_box(self):
        """Construct the right hand box to pack into the main model-free box.

        @return:    The right hand box element containing all model-free GUI elements (excluding the bitmap) to pack into the main model-free box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_frame_title(box)

        # Add the relaxation data input GUI element.
        self.add_relax_data_input(box)

        # Add the model-free models GUI element.
        self.add_mf_models(box)

        # Add the model selection GUI element.
        self.add_modsel_method(box)

        # Add the PDB file selection GUI element.
        self.add_pdb_selection(box)

        # Add the unresolved spins GUI element.
        self.add_unresolved_spins(box)

        # Add the results directory GUI element.
        self.add_results_dir(box)

        # Add the execution GUI element.
        self.add_execute_relax(box)

        # Return the packed box.
        return box


    def check_entries(self):
        check = False
        counter = 0

        # check frq 1
        if not self.modelfreefreq1.GetValue() == '':
            counter = counter + 1
        if not self.m_noe_1.GetValue() == '':
            counter = counter + 1
        if not self.m_r1_1.GetValue() == '':
            counter = counter + 1
        if not self.m_r2_1.GetValue() == '':
            counter = counter + 1

        # check frq 1
        if not self.modelfreefreq2.GetValue() == '':
            counter = counter + 1
        if not self.m_noe_2.GetValue() == '':
            counter = counter + 1
        if not self.m_r1_2.GetValue() == '':
            counter = counter + 1
        if not self.m_r2_2.GetValue() == '':
            counter = counter + 1

        # check frq 1
        if not self.modelfreefreq3.GetValue() == '':
            counter = counter + 1
        if not self.m_noe_3.GetValue() == '':
            counter = counter + 1
        if not self.m_r1_3.GetValue() == '':
            counter = counter + 1
        if not self.m_r2_3.GetValue() == '':
            counter = counter + 1

        # two field strength ok
        if counter == 8:
            check = True
            print '\n\n\nTwo different field strength detected !!\n\n\n'

        # three field strength ok
        elif counter == 12:
            check = True
            print '\n\n\nThree different field strength detected !!\n\n\n'

        # missing data
        else:
            missing_data()

        return check


    def exec_model_free(self, event):     # start model-free calculation by relax
        checkpoint = self.check_entries()
        if checkpoint == False:
            which_model = None
        else:
            which_model = self.whichmodel(False)

        # start individual calculations
        if not which_model == None:

            if not which_model == 'full':
                if not which_model == 'final':

                    # run sphere, prolate, oblate or ellipsoid
                    enable_models = False
                    enable_models = start_modelfree(self, which_model, False, global_setting, file_setting, sequencefile)

                    if enable_models:
                        self.local_tm_flag = True
                else:

                    # run final run
                    results_for_table = startmodelfree(self, which_model, False, global_setting, file_setting, sequencefile)

                    # import global variables for results table
                    global table_residue
                    global table_model
                    global table_s2
                    global table_rex
                    global table_te

                    # set global results variables
                    table_residue = results_for_table[0]
                    table_model = results_for_table[1]
                    table_s2 = results_for_table[2]
                    table_rex = results_for_table[3]
                    table_te = results_for_table[4]


            # start full automatic model-free analysis
            if which_model == 'full':
                model1 = start_modelfree(self, 'local_tm', True, global_setting, file_setting, sequencefile)    # execute local_tm
                if model1 == 'successful':
                    model2 = start_modelfree(self, 'sphere', True, global_setting, file_setting, sequencefile)        # execute sphere
                    if model2 == 'successful':
                        model3 = start_modelfree(self, 'prolate', True, global_setting, file_setting, sequencefile)         # execute prolate
                        if model3 == 'successful':
                            model4 = start_modelfree(self, 'oblate', True, global_setting, file_setting, sequencefile)         # execute oblate
                            if model4 == 'successful':
                                model5 = start_modelfree(self, 'ellipsoid', True, global_setting, file_setting, sequencefile)      # execute ellipsoid
                                if model5 == 'successful':
                                    model6 = start_modelfree(self, 'final', False, global_setting, file_setting, sequencefile)        # execute final analysis
        event.Skip()


    def model_noe1(self, event): # load noe1
        backup = self.m_noe_1.GetValue()
        self.paramfiles1[0] = openfile('Select NOE file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles1[0] == None:
            self.paramfiles1[0] = backup
        self.m_noe_1.SetValue(self.paramfiles1[0])
        event.Skip()


    def model_noe2(self, event): # load noe1
        backup = self.m_noe_2.GetValue()
        self.paramfiles2[0] = openfile('Select NOE file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles2[0] == None:
            self.paramfiles2[0] = backup
        self.m_noe_2.SetValue(self.paramfiles2[0])
        event.Skip()


    def model_noe3(self, event): # load noe1
        backup = self.m_noe_3.GetValue()
        self.paramfiles3[0] = openfile('Select NOE file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles3[0] == None:
            self.paramfiles3[0] = backup
        self.m_noe_3.SetValue(self.paramfiles3[0])
        event.Skip()


    def model_r11(self, event): #
        backup = self.m_r1_1.GetValue()
        self.paramfiles1[1] = openfile('Select R1 file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles1[1] == None:
            self.paramfiles1[1] = backup
        self.m_r1_1.SetValue(self.paramfiles1[1])
        event.Skip()


    def model_r12(self, event): #
        backup = self.m_r1_2.GetValue()
        self.paramfiles2[1] = openfile('Select R1 file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles2[1] == None:
            self.paramfiles2[1] = backup
        self.m_r1_2.SetValue(self.paramfiles2[1])
        event.Skip()


    def model_r13(self, event):
        backup = self.m_r1_3.GetValue()
        self.paramfiles3[1] = openfile('Select R1 file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles3[1] == None:
            self.paramfiles3[1] = backup
        self.m_r1_3.SetValue(self.paramfiles3[1])
        event.Skip()


    def model_r21(self, event): #
        backup = self.m_r2_1.GetValue()
        self.paramfiles1[2] = openfile('Select R2 file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles1[2] == None:
            self.paramfiles1[2] = backup
        self.m_r2_1.SetValue(self.paramfiles1[2])
        event.Skip()


    def model_r22(self, event): #
        backup = self.m_r2_2.GetValue()
        self.paramfiles2[2] = openfile('Select R2 file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles2[2] == None:
            self.paramfiles2[2] = backup
        self.m_r2_2.SetValue(self.paramfiles2[2])
        event.Skip()


    def model_r23(self, event):
        backup = self.m_r2_3.GetValue()
        self.paramfiles3[2] = openfile('Select R2 file', self.resultsdir_r21_copy_2.GetValue(), '*.*', 'all files (*.*)|*.*')
        if self.paramfiles3[2] == None:
            self.paramfiles3[2] = backup
        self.m_r2_3.SetValue(self.paramfiles3[2])
        event.Skip()


    def open_model_results_exe(self, event):    # open model-free results
        choice = self.list_modelfree.GetStringSelection()
        model_result = [table_residue, table_model, table_s2, table_rex, table_te] # relax results values
        see_results(choice, model_result)
        event.Skip()


    def resdir_modelfree(self, event):
        backup = self.resultsdir_r21_copy_2.GetValue()
        self.results_dir_model = opendir('Select results directory', backup)
        if self.results_dir_model == None:
            self.results_dir_model = backup
        self.resultsdir_r21_copy_2.SetValue(self.results_dir_model)
        event.Skip()


    def sel_aic(self, event):
        selection = "AIC"
        event.Skip()


    def sel_bic(self, event):
        selection = "BIC"
        event.Skip()


    def whichmodel(self, is_local_tm):
        selection = None
        dlg = Select_tensor(None, -1, "", local_tm_flag=is_local_tm)
        dlg.ShowModal()
        return selection
