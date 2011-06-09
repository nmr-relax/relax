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
"""Module for the automatic model-free protocol frame."""

# Python module imports.
from os import getcwd, sep
from string import replace, split
import sys
import thread
import time
import wx

# relax module imports.
from auto_analyses import dauvergne_protocol
from data import Relax_data_store; ds = Relax_data_store()
from doc_builder import LIST, PARAGRAPH, SECTION, SUBSECTION, TITLE
from relax_io import DummyFileObject
from status import Status; status = Status()


# relax GUI module imports.
from gui.about import About_base
from gui.analyses.base import Base_frame
from gui.analyses.results_analysis import model_free_results, see_results
from gui.analyses.select_model_calc import Select_tensor
from gui.base_classes import Container
from gui.components.conversion import str_to_float
from gui.controller import Redirect_text, Thread_container
from gui.derived_wx_classes import StructureTextCtrl
from gui.filedialog import opendir, openfile
from gui.message import error_message, missing_data
from gui import paths


class About_window(About_base):
    """The model-free about window."""

    # The relax background colour.
    colour1 = '#e5feff'
    colour2 = '#88cbff'

    # Dimensions.
    dim_x = 800
    dim_y = 800
    max_y = 2500

    # Spacer size (px).
    border = 10

    # Window style.
    style = wx.DEFAULT_DIALOG_STYLE

    # Destroy on clicking.
    DESTROY_ON_CLICK = False

    def __init__(self, parent):
        """Set up the user function class."""

        # Execute the base class method.
        super(About_window, self).__init__(parent, id=-1, title="Automatic model-free analysis about window")


    def build_widget(self):
        """Build the dialog using the dauvergne_protocol docstring."""

        # The text width (number of characters).
        width = 120

        # Loop over the lines.
        for i in range(len(dauvergne_protocol.doc)):
            # The level and text.
            level, text = dauvergne_protocol.doc[i]

            # The title.
            if level == TITLE:
                self.draw_title(text, point_size=18)

            # The section.
            elif level == SECTION:
                self.draw_title(text, point_size=14)

            # The section.
            elif level == SUBSECTION:
                self.draw_title(text, point_size=12)

            # Paragraphs.
            elif level == PARAGRAPH:
                self.draw_wrapped_text(text, width=width)

            # Lists.
            elif level == LIST:
                # Start of list.
                if i and dauvergne_protocol.doc[i-1][0] != LIST:
                    self.offset(10)

                # The text.
                self.draw_wrapped_text("    - %s" % text, width=width)

                # End of list.
                if i < len(dauvergne_protocol.doc) and dauvergne_protocol.doc[i+1][0] == PARAGRAPH:
                    self.offset(10)


    def virtual_size(self):
        """Determine the virtual size of the window."""

        # A temp window.
        frame = wx.Frame(None, -1)
        win = wx.Window(frame)

        # A temp DC.
        self.dc = wx.ClientDC(win)

        # Build the widget within the temp DC.
        self.virt_x = self.dim_x
        self.build_widget()

        # The virtual size.
        self.virt_x = self.text_max_x + 2*self.border + 20
        size_y = self.offset()
        remainder = size_y - size_y / self.SCROLL_RATE * self.SCROLL_RATE
        self.virt_y = size_y + remainder + self.border

        # Destroy the temporary objects.
        frame.Destroy()
        win.Destroy()
        self.dc.Destroy()

        # Reset the offset.
        self.offset(-self.offset())


class Auto_model_free(Base_frame):
    def __init__(self, gui, notebook):
        """Build the automatic model-free protocol GUI element.

        @param gui:         The main GUI class.
        @type gui:          gui.relax_gui.Main instance
        @param notebook:    The notebook to pack this frame into.
        @type notebook:     wx.Notebook instance
        """

        # Store the main class.
        self.gui = gui

        # Generate a storage container in the relax data store, and alias it for easy access.
        self.data = ds.relax_gui.analyses.add('model-free')

        # Model-free variables.
        self.data.model_source = getcwd()
        self.data.model_save = getcwd()
        self.data.selection = "AIC"
        self.data.model_toggle = [True]*10
        self.data.nmrfreq1 = 600
        self.data.nmrfreq2 = 800
        self.data.nmrfreq3 = 900
        self.data.paramfiles1 = ["", "", ""]
        self.data.paramfiles2 = ["", "", ""]
        self.data.paramfiles3 = ["", "", ""]
        self.data.unresolved = ''
        self.data.structure_file = ''
        self.data.results_dir_model = getcwd()
        self.data.max_iter = "30"

        # The parent GUI element for this class.
        self.parent = wx.Panel(notebook, -1)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        main_box = self.build_main_box()
        self.parent.SetSizer(main_box)

        # Set the frame font size.
        self.parent.SetFont(self.gui.font_small)


    def _about(self, event):
        """The about window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the dialog.
        dialog = About_window(self.parent)

        # Show the dialog.
        dialog.Show()


    def add_execute_relax(self, box):
        """Create and add the relax execution GUI element to the given box.

        @param box:     The box element to pack the relax execution GUI element into.
        @type box:      wx.BoxSizer instance
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
        button.SetName('hello')
        button.SetSize(button.GetBestSize())
        self.gui.Bind(wx.EVT_BUTTON, self.automatic_protocol_controller, button)
        sizer.Add(button, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 1, wx.ALIGN_RIGHT, 0)


    def add_max_iterations(self, box):
        """Create and add the model-free maximum interation GUI element to the given box.

        @param box:     The box element to pack the model-free maximum iteration GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Sizer.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Text.
        label_maxiter = wx.StaticText(self.parent, -1, "Maximum interations")
        label_maxiter.SetMinSize((240, 17))
        label_maxiter.SetFont(self.gui.font_normal)
        sizer.Add(label_maxiter, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spinner.
        self.max_iter = wx.SpinCtrl(self.parent, -1, self.data.max_iter, min=25, max=100)
        sizer.Add(self.max_iter, 0, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Add the element to the box.
        box.Add(sizer, 1, wx.EXPAND, 0)


    def add_mf_models(self, box):
        """Create and add the model-free model picking GUI element to the given box.

        @param box:     The box element to pack the model-free model picking GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # The elements.
        label = wx.StaticText(self.parent, -1, "Select model-free models (default = all):")
        label.SetFont(self.gui.font_normal)
        self.m0 = wx.ToggleButton(self.parent, -1, "m0")
        self.m1 = wx.ToggleButton(self.parent, -1, "m1")
        self.m2 = wx.ToggleButton(self.parent, -1, "m2")
        self.m3 = wx.ToggleButton(self.parent, -1, "m3")
        self.m4 = wx.ToggleButton(self.parent, -1, "m4")
        self.m5 = wx.ToggleButton(self.parent, -1, "m5")
        self.m6 = wx.ToggleButton(self.parent, -1, "m6")
        self.m7 = wx.ToggleButton(self.parent, -1, "m7")
        self.m8 = wx.ToggleButton(self.parent, -1, "m8")
        self.m9 = wx.ToggleButton(self.parent, -1, "m9")

        # Properties.
        self.m0.SetMinSize((70, 25))
        self.m0.SetFont(self.gui.font_button)
        self.m0.SetToolTipString("{}")
        self.m0.SetValue(1)
        self.m1.SetMinSize((70, 25))
        self.m1.SetFont(self.gui.font_button)
        self.m1.SetToolTipString("{S2}")
        self.m1.SetValue(1)
        self.m2.SetMinSize((70, 25))
        self.m2.SetFont(self.gui.font_button)
        self.m2.SetToolTipString("{S2, te}")
        self.m2.SetValue(1)
        self.m3.SetMinSize((70, 25))
        self.m3.SetFont(self.gui.font_button)
        self.m3.SetToolTipString("{S2, Rex}")
        self.m3.SetValue(1)
        self.m4.SetMinSize((70, 25))
        self.m4.SetFont(self.gui.font_button)
        self.m4.SetToolTipString("{S2, te, Rex}")
        self.m4.SetValue(1)
        self.m5.SetMinSize((70, 25))
        self.m5.SetFont(self.gui.font_button)
        self.m5.SetToolTipString("{S2, S2f, ts}")
        self.m5.SetValue(1)
        self.m6.SetMinSize((70, 25))
        self.m6.SetFont(self.gui.font_button)
        self.m6.SetToolTipString("{S2, tf, S2f, ts}")
        self.m6.SetValue(1)
        self.m7.SetMinSize((70, 25))
        self.m7.SetFont(self.gui.font_button)
        self.m7.SetToolTipString("{S2, S2f, ts, Rex}")
        self.m7.SetValue(1)
        self.m8.SetMinSize((70, 25))
        self.m8.SetFont(self.gui.font_button)
        self.m8.SetToolTipString("{S2, tf, S2f, ts, Rex}")
        self.m8.SetValue(1)
        self.m9.SetMinSize((70, 25))
        self.m9.SetFont(self.gui.font_button)
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
        box.Add(label, 0, wx.TOP|wx.ADJUST_MINSIZE, 10)
        box.Add(sizer_20, 1, wx.EXPAND, 0)


    def add_relax_data_input(self, box):
        """Create and add the relaxation data input GUI element to the given box.

        @param box:     The box element to pack the relax data input GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Create the panel.
        panel_4_copy_1 = wx.Panel(self.parent, -1)
        panel_4_copy = wx.Panel(self.parent, -1)
        panel_4 = wx.Panel(self.parent, -1)

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
        model_noe_1.SetFont(self.gui.font_smaller)
        label_8_copy.SetMinSize((80, 17))
        self.m_r1_1.SetMinSize((120, 20))
        model_r1_1.SetMinSize((20, 20))
        model_r1_1.SetFont(self.gui.font_smaller)
        label_8_copy_copy.SetMinSize((80, 17))
        self.m_r2_1.SetMinSize((120, 20))
        model_r2_1.SetMinSize((20, 20))
        model_r2_1.SetFont(self.gui.font_smaller)
        label_7_copy.SetMinSize((80, 17))
        self.modelfreefreq2.SetMinSize((80, 20))
        label_8_copy_1.SetMinSize((80, 17))
        self.m_noe_2.SetMinSize((120, 20))
        model_noe_2.SetMinSize((20, 20))
        model_noe_2.SetFont(self.gui.font_smaller)
        label_8_copy_copy_1.SetMinSize((80, 17))
        self.m_r1_2.SetMinSize((120, 20))
        model_r1_2.SetMinSize((20, 20))
        model_r1_2.SetFont(self.gui.font_smaller)
        label_8_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_2.SetMinSize((120, 20))
        model_r2_2.SetMinSize((20, 20))
        model_r2_2.SetFont(self.gui.font_smaller)
        label_7_copy_copy.SetMinSize((80, 17))
        self.modelfreefreq3.SetMinSize((80, 20))
        label_8_copy_1_copy.SetMinSize((80, 17))
        self.m_noe_3.SetMinSize((120, 20))
        model_noe_3.SetMinSize((20, 20))
        model_noe_3.SetFont(self.gui.font_smaller)
        label_8_copy_copy_1_copy.SetMinSize((80, 17))
        self.m_r1_3.SetMinSize((120, 20))
        model_r1_3.SetMinSize((20, 20))
        model_r1_3.SetFont(self.gui.font_smaller)
        label_8_copy_copy_copy_copy.SetMinSize((80, 17))
        self.m_r2_3.SetMinSize((120, 20))
        model_r2_3.SetMinSize((20, 20))
        model_r2_3.SetFont(self.gui.font_smaller)

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


    def assemble_data(self):
        """Assemble the data required for the dAuvernge_protocol class.

        See the docstring for auto_analyses.dauvernge_protocol for details.  All data is taken from the relax data store, so data upload from the GUI to there must have been previously performed.

        @return:    A container with all the data required for dAuvernge_protocol, i.e. its keyword arguments mf_models, local_tm_models, pdb_file, seq_args, het_name, relax_data, unres, exclude, bond_length, csa, hetnuc, proton, grid_inc, min_algor, mc_num, conv_loop.
        @rtype:     class instance
        """

        # The data container.
        data = Container()

        # The model-free models (do not change these unless absolutely necessary).
        data.mf_models = []
        data.local_tm_models = []
        for i in range(len(self.data.model_toggle)):
            if self.data.model_toggle[i]:
                data.mf_models.append('m%i' % i)
                data.local_tm_models.append('tm%i' % i)

        # Structure File
        data.structure_file = self.data.structure_file

        # Set Structure file as None if a structure file is loaded.
        if data.structure_file == '!!! Sequence file selected !!!':
            data.structure_file = None

        # Name of heteronucleus in PDB File.
        data.het_name = 'N'

        # Assign parameter file to sequence file.
        if not self.data.paramfiles1[0] == '':     # NOE file of frq 1
            sequence_file = self.data.paramfiles1[0]
        if not self.data.paramfiles1[1] == '':     # R1 file of frq 1
            sequence_file = self.data.paramfiles1[1]
        if not self.data.paramfiles1[2] == '':     # R2 file of frq 1
            sequence_file = self.data.paramfiles1[2]

        # Alias the free file format data structure.
        format = ds.relax_gui.free_file_format

        # The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        data.seq_args = [sequence_file, None, format.mol_name_col, format.res_num_col, format.res_name_col, format.spin_num_col, format.spin_name_col, format.sep]

        # Import golbal settings.
        global_settings = ds.relax_gui.global_setting

        # Hetero nucleus name.
        if 'N' in global_settings[2]:
            data.hetnuc = '15N'
        elif 'C' in global_settings[2]:
            data.hetnuc = '13C'
        else:
            data.hetnuc = global_settings[2]

        # Proton name.
        if '2' in global_settings[3]:
            data.proton = '2H'
        else:
            data.proton = '1H'

        # Increment size.
        data.inc = int(global_settings[4])

        # The optimisation technique.
        data.min_algor = global_settings[5]

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        data.mc_num = int(global_settings[6])

        # The bond length, CSA values.
        data.bond_length = str_to_float(global_settings[0])
        data.csa = str_to_float(global_settings[1])

        # The relaxation data (data type, frequency label, frequency, file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, data_col, error_col, sep).  These are the arguments to the relax_data.read() user function, please see the documentation for that function for more information.
        data.relax_data = []
        for i in range(3):
            # The objects.
            frq = getattr(self.data, 'nmrfreq%i' % (i+1))
            files = getattr(self.data, 'paramfiles%i' % (i+1))

            # Data has not been given, so skip this entry.
            if frq == '':
                continue

            # Append the relaxation data if present.
            if not files[1] == '':
                data.relax_data.append(['R1', str(frq), float(frq)*1e6, files[1], None, format.mol_name_col, format.res_num_col, format.res_name_col, format.spin_num_col, format.spin_name_col, format.data_col, format.err_col, format.sep])
            if not files[2] == '':
                data.relax_data.append(['R2', str(frq), float(frq)*1e6, files[2], None, format.mol_name_col, format.res_num_col, format.res_name_col, format.spin_num_col, format.spin_name_col, format.data_col, format.err_col, format.sep])
            if not files[0] == '':
                data.relax_data.append(['NOE', str(frq), float(frq)*1e6, files[0], None, format.mol_name_col, format.res_num_col, format.res_name_col, format.spin_num_col, format.spin_name_col, format.data_col, format.err_col, format.sep])

        # Unresolved resiudes
        file = DummyFileObject()
        entries = self.data.unresolved
        entries = replace(entries, ',', '\n')
        file.write(entries)
        file.close()
        data.unres = file

        # A file containing a list of spins which can be dynamically excluded at any point within the analysis (when set to None, this variable is not used).
        data.exclude = None

        # Automatic looping over all rounds until convergence (must be a boolean value of True or False).
        data.conv_loop = True

        # Results directory.
        data.save_dir = self.data.results_dir_model

        # Number of maximum iterations.
        data.max_iter = self.data.max_iter

        # Return the container.
        return data


    def automatic_protocol_controller(self, event):
        """Set up, execute, and process the automatic model-free protocol.

        @param event:   The wx event.
        @type event:    wx event
        """

        # relax execution lock.
        status = Status()
        if status.exec_lock.locked():
            error_message("relax is currently executing.", "relax execution lock")
            event.Skip()
            return

        # The required data has not been set up correctly or has not all been given, so clean up and exit.
        if not self.check_entries():
            event.Skip()
            return

        # PDB file is given.
        if str(self.field_structure.GetValue()) in ['', 'please insert .pdb file']:
            missing_data(missing=['No PDB file selected.'])
            return

        # Synchronise the frame data to the relax data store.
        self.sync_ds(upload=True)

        # The global model.
        which_model = self.choose_global_model(False)

        # Display the relax controller.
        if not status.debug:
            self.gui.controller.Show()

        # Cancel.
        if which_model == None:
            return

        # Solve for all global models.
        elif which_model == 'full':
            # The global model list.
            global_models = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid', 'final']

        # Any global model selected.
        else:
            global_models = [which_model]

        # Run the models.
        self.execute(global_models=global_models, automatic=False)

        # Skip the event.
        event.Skip()


    def build_main_box(self):
        """Construct the highest level box to pack into the automatic model-free analysis frame.

        @return:    The main box element containing all model-free GUI elements to pack directly into the automatic model-free analysis frame.
        @rtype:     wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        box = wx.BoxSizer(wx.HORIZONTAL)

        # Build the left hand box.
        left_box = wx.BoxSizer(wx.VERTICAL)

        # Add the model-free bitmap picture.
        bitmap = wx.StaticBitmap(self.parent, -1, wx.Bitmap(paths.IMAGE_PATH+'modelfree.png', wx.BITMAP_TYPE_ANY))
        left_box.Add(bitmap, 0, wx.ALL, 0)

        # A spacer.
        left_box.AddStretchSpacer()

        # A button sizer, with some initial spacing.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.AddSpacer(10)

        # An about button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self.parent, -1, None, "About")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.about, wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Information about this automatic analysis")

        # Bind the click.
        self.parent.Bind(wx.EVT_BUTTON, self._about, button)

        # A cursor for the button.
        cursor = wx.StockCursor(wx.CURSOR_QUESTION_ARROW)
        button.SetCursor(cursor)

        # Pack the button.
        button_sizer.Add(button, 0, 0, 0)
        left_box.Add(button_sizer, 0, wx.ALL, 0)

        # Spacer.
        left_box.AddSpacer(10)

        # Add to the main box.
        box.Add(left_box, 0, wx.ADJUST_MINSIZE, 0)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 1, 0, 0)

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
        self.add_title(box, "Setup for model-free analysis")

        # Add the relaxation data input GUI element.
        self.add_relax_data_input(box)

        # Add the model-free models GUI element.
        self.add_mf_models(box)

        # Add maximum interation selector.
        self.add_max_iterations(box)

        # Add the PDB file selection GUI element.
        self.field_structure = self.add_text_sel_element(box, self.parent, text="Structure file (.pdb)", default=str(self.gui.structure_file_pdb_msg), control=StructureTextCtrl, width_text=230, width_control=350, width_button=103, fn='open_file', editable=False, button=True)

        # Add the unresolved spins GUI element.
        self.field_unresolved = self.add_text_sel_element(box, self.parent, text="Unresolved residues", width_text=230, width_control=350, width_button=103)

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self.parent, text="Results directory", default=self.data.results_dir_model, width_text=230, width_control=350, width_button=103, fn=self.resdir_modelfree, button=True)

        # Add the execution GUI element.
        self.add_execute_relax(box)

        # Return the packed box.
        return box


    def check_entries(self):
        check = False
        counter_frq = 0
        counter_noe = 0
        counter_r1 = 0
        counter_r2 = 0

        # check frq 1
        if not self.modelfreefreq1.GetValue() == '':
            counter_frq = counter_frq + 1
        if not self.m_noe_1.GetValue() == '':
            counter_noe = counter_noe + 1
        if not self.m_r1_1.GetValue() == '':
            counter_r1 = counter_r1 + 1
        if not self.m_r2_1.GetValue() == '':
            counter_r2 = counter_r2 + 1

        # check frq 1
        if not self.modelfreefreq2.GetValue() == '':
            counter_frq = counter_frq + 1
        if not self.m_noe_2.GetValue() == '':
            counter_noe = counter_noe + 1
        if not self.m_r1_2.GetValue() == '':
            counter_r1 = counter_r1 + 1
        if not self.m_r2_2.GetValue() == '':
            counter_r2 = counter_r2 + 1

        # check frq 1
        if not self.modelfreefreq3.GetValue() == '':
            counter_frq = counter_frq + 1
        if not self.m_noe_3.GetValue() == '':
            counter_noe = counter_noe + 1
        if not self.m_r1_3.GetValue() == '':
            counter_r1 = counter_r1 + 1
        if not self.m_r2_3.GetValue() == '':
            counter_r2 = counter_r2 + 1

        # each parameter has to be present at least in doublicates
        if counter_frq > 1 and counter_noe > 1 and counter_r1 > 1 and counter_r2 > 1:
            check = True

        # missing data
        else:
            missing_data()

        return check


    def choose_global_model(self, local_tm_complete=False):
        """Select the individual global models to solve, or all automatically.

        @keyword local_tm_complete: A flag specifying if the local tm global model has been solved already.
        @type local_tm_complete:    bool
        @return:                    The global model selected, or 'full' for all.
        @rtype:                     str
        """

        # The dialog.
        dlg = Select_tensor(None, -1, "", local_tm_flag=True)
        dlg.ShowModal()

        # Return the choice.
        return dlg.selection


    def execute(self, global_models=None, automatic=True):
        """Execute the calculations by running execute_thread() within a thread.

        @keyword global_models: The list of global models to solve.  The elements must be one of 'local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid', or 'final'.
        @type global_models:    list of str
        """

        # The thread object storage.
        self.gui.calc_threads.append(Thread_container())
        thread_cont = self.gui.calc_threads[-1]

        # Start the thread.
        if status.debug:
            self.execute_thread(global_models=global_models, automatic=automatic)
        else:
            id = thread.start_new_thread(self.execute_thread, (), {'global_models': global_models, 'automatic': automatic})

            # Add the thread info to the container.
            thread_cont.id = id
            thread_cont.analysis_type = 'model-free'
            thread_cont.global_models = global_models


    def execute_thread(self, global_models=None, automatic=True):
        """Execute the calculation in a thread.

        @keyword global_models: The list of global models to solve.  The elements must be one of 'local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid', or 'final'.
        @type global_models:    list of str
        """

        # Loop over the models.
        for global_model in global_models:
            # Assemble all the data needed for the dAuvergne_protocol class.
            data = self.assemble_data()

            # Value for progress bar during Monte Carlo simulation.
            self.gui.calc_threads[-1].progress = 5.0

            # Controller.
            if not status.debug:
                # Redirect relax output and errors to the controller.
                redir = Redirect_text(self.gui.controller)
                sys.stdout = redir
                sys.stderr = redir

                # Print a header in the controller.
                str = 'Starting model-free calculation'
                wx.CallAfter(self.gui.controller.log_panel.AppendText, ('\n\n\n' + str + '\n' + '-'*len(str) + '\n\n') )
                time.sleep(0.5)

            # Start the protocol.
            dauvergne_protocol.dAuvergne_protocol(save_dir=data.save_dir, diff_model=global_model, mf_models=data.mf_models, local_tm_models=data.local_tm_models, pdb_file=data.structure_file, seq_args=data.seq_args, het_name=data.het_name, relax_data=data.relax_data, unres=data.unres, exclude=data.exclude, bond_length=data.bond_length, csa=data.csa, hetnuc=data.hetnuc, proton=data.proton, grid_inc=data.inc, min_algor=data.min_algor, mc_num=data.mc_num, max_iter=data.max_iter, conv_loop=data.conv_loop)

            # Feedback about success.
            str = 'Successfully calculated the %s global model.' % global_model
            wx.CallAfter(self.gui.controller.log_panel.AppendText, '\n\n' + '_'*len(str) + '\n\n' + str + '\n' + '_'*len(str))

            # Create the results file.
            if global_model == 'final':
                # Feedback.
                wx.CallAfter(self.gui.controller.log_panel.AppendText, '\n\nCreating results files\n\n')
                time.sleep(3)

                results_analysis = model_free_results(self, data.save_dir, data.structure_file)

                # Add grace plots to results tab.
                directory = data.save_dir+sep+'final'
                self.gui.list_modelfree.Append(directory+sep+'grace'+sep+'s2.agr')
                self.gui.list_modelfree.Append(directory+sep+'Model-free_Results.csv')
                self.gui.list_modelfree.Append(directory+sep+'diffusion_tensor.pml')
                self.gui.list_modelfree.Append(directory+sep+'s2.pml')
                self.gui.list_modelfree.Append(directory+sep+'rex.pml')
                self.gui.list_modelfree.Append('Table_of_Results')

                # Add results to relax data storage.
                ds.relax_gui.results_model_free.append(directory+sep+'grace'+sep+'s2.agr')
                ds.relax_gui.results_model_free.append(directory+sep+'Model-free_Results.txt')
                ds.relax_gui.results_model_free.append(directory+sep+'diffusion_tensor.pml')
                ds.relax_gui.results_model_free.append(directory+sep+'s2.pml')
                ds.relax_gui.results_model_free.append(directory+sep+'rex.pml')
                ds.relax_gui.results_model_free.append('Table_of_Results')

                # set global results variables
                ds.relax_gui.table_residue = results_analysis[0]
                ds.relax_gui.table_model = results_analysis[1]
                ds.relax_gui.table_s2 = results_analysis[2]
                ds.relax_gui.table_rex = results_analysis[3]
                ds.relax_gui.table_te = results_analysis[4]

        # Return successful value to automatic mode to proceed to next step.
        if automatic == True:
            return 'successful'

        # Enable m1-m5.
        if not automatic:
            if global_model == 'local_tm':
                # enable m1 - m5 to choose for calculation
                return True


    def link_data(self, data):
        """Re-alias the storage container in the relax data store.
        @keyword data:      The data storage container.
        @type data:         class instance
        """

        # Alias.
        self.data = data


    def model_noe1(self, event): # load noe1
        backup = self.m_noe_1.GetValue()
        self.data.paramfiles1[0] = openfile(msg='Select NOE file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles1[0] == None:
            self.data.paramfiles1[0] = backup
        self.m_noe_1.SetValue(self.data.paramfiles1[0])
        self.m_noe_1.SetInsertionPoint(len(self.data.paramfiles1[0]))
        event.Skip()


    def model_noe2(self, event): # load noe1
        backup = self.m_noe_2.GetValue()
        self.data.paramfiles2[0] = openfile(msg='Select NOE file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles2[0] == None:
            self.data.paramfiles2[0] = backup
        self.m_noe_2.SetValue(self.data.paramfiles2[0])
        self.m_noe_2.SetInsertionPoint(len(self.data.paramfiles2[0]))
        event.Skip()


    def model_noe3(self, event): # load noe1
        backup = self.m_noe_3.GetValue()
        self.data.paramfiles3[0] = openfile(msg='Select NOE file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles3[0] == None:
            self.data.paramfiles3[0] = backup
        self.m_noe_3.SetValue(self.data.paramfiles3[0])
        self.m_noe_3.SetInsertionPoint(len(self.data.paramfiles3[0]))
        event.Skip()


    def model_r11(self, event): #
        backup = self.m_r1_1.GetValue()
        self.data.paramfiles1[1] = openfile(msg='Select R1 file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles1[1] == None:
            self.data.paramfiles1[1] = backup
        self.m_r1_1.SetValue(self.data.paramfiles1[1])
        self.m_r1_1.SetInsertionPoint(len(self.data.paramfiles1[1]))
        event.Skip()


    def model_r12(self, event): #
        backup = self.m_r1_2.GetValue()
        self.data.paramfiles2[1] = openfile(msg='Select R1 file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles2[1] == None:
            self.data.paramfiles2[1] = backup
        self.m_r1_2.SetValue(self.data.paramfiles2[1])
        self.m_r1_2.SetInsertionPoint(len(self.data.paramfiles2[1]))
        event.Skip()


    def model_r13(self, event):
        backup = self.m_r1_3.GetValue()
        self.data.paramfiles3[1] = openfile(msg='Select R1 file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles3[1] == None:
            self.data.paramfiles3[1] = backup
        self.m_r1_3.SetValue(self.data.paramfiles3[1])
        self.m_r1_3.SetInsertionPoint(len(self.data.paramfiles3[1]))
        event.Skip()


    def model_r21(self, event): #
        backup = self.m_r2_1.GetValue()
        self.data.paramfiles1[2] = openfile(msg='Select R2 file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles1[2] == None:
            self.data.paramfiles1[2] = backup
        self.m_r2_1.SetValue(self.data.paramfiles1[2])
        self.m_r2_1.SetInsertionPoint(len(self.data.paramfiles1[2]))
        event.Skip()


    def model_r22(self, event): #
        backup = self.m_r2_2.GetValue()
        self.data.paramfiles2[2] = openfile(msg='Select R2 file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles2[2] == None:
            self.data.paramfiles2[2] = backup
        self.m_r2_2.SetValue(self.data.paramfiles2[2])
        self.m_r2_2.SetInsertionPoint(len(self.data.paramfiles2[2]))
        event.Skip()


    def model_r23(self, event):
        backup = self.m_r2_3.GetValue()
        self.data.paramfiles3[2] = openfile(msg='Select R2 file', filetype='*.*', default='all files (*.*)|*')
        if self.data.paramfiles3[2] == None:
            self.data.paramfiles3[2] = backup
        self.m_r2_3.SetValue(self.data.paramfiles3[2])
        self.m_r2_3.SetInsertionPoint(len(self.data.paramfiles3[2]))
        event.Skip()


    def open_model_results_exe(self, event):    # open model-free results
        choice = self.list_modelfree.GetStringSelection()
        model_result = [ds.relax_gui.table_residue, ds.relax_gui.table_model, ds.relax_gui.table_s2, ds.relax_gui.table_rex, ds.relax_gui.table_te] # relax results values
        see_results(choice, model_result)
        event.Skip()


    def resdir_modelfree(self, event):
        backup = self.field_results_dir.GetValue()
        self.data.results_dir_model = opendir('Select results directory', backup)
        if self.data.results_dir_model == None:
            self.data.results_dir_model = backup
        self.field_results_dir.SetValue(self.data.results_dir_model)
        event.Skip()


    def sel_aic(self, event):
        selection = "AIC"
        event.Skip()


    def sel_bic(self, event):
        selection = "BIC"
        event.Skip()


    def sync_ds(self, upload=False):
        """Synchronise the analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # Relaxation data input.
        if upload:
            # First frequency.
            self.data.nmrfreq1 = str(self.modelfreefreq1.GetValue())
            self.data.paramfiles1[0] = str(self.m_noe_1.GetValue())
            self.data.paramfiles1[1] = str(self.m_r1_1.GetValue())
            self.data.paramfiles1[2] = str(self.m_r2_1.GetValue())

            # Second frequency.
            self.data.nmrfreq2 = str(self.modelfreefreq2.GetValue())
            self.data.paramfiles2[0] = str(self.m_noe_2.GetValue())
            self.data.paramfiles2[1] = str(self.m_r1_2.GetValue())
            self.data.paramfiles2[2] = str(self.m_r2_2.GetValue())

            # Third frequency.
            self.data.nmrfreq3 = str(self.modelfreefreq3.GetValue())
            self.data.paramfiles3[0] = str(self.m_noe_3.GetValue())
            self.data.paramfiles3[1] = str(self.m_r1_3.GetValue())
            self.data.paramfiles3[2] = str(self.m_r2_3.GetValue())
        else:
            # First frequency.
            self.modelfreefreq1.SetValue(str(self.data.nmrfreq1))
            self.m_noe_1.SetValue(str(self.data.paramfiles1[0]))
            self.m_r1_1.SetValue(str(self.data.paramfiles1[1]))
            self.m_r2_1.SetValue(str(self.data.paramfiles1[2]))

            # Second frequency.
            self.modelfreefreq2.SetValue(str(self.data.nmrfreq2))
            self.m_noe_2.SetValue(str(self.data.paramfiles2[0]))
            self.m_r1_2.SetValue(str(self.data.paramfiles2[1]))
            self.m_r2_2.SetValue(str(self.data.paramfiles2[2]))

            # Third frequency.
            self.modelfreefreq3.SetValue(str(self.data.nmrfreq3))
            self.m_noe_3.SetValue(str(self.data.paramfiles3[0]))
            self.m_r1_3.SetValue(str(self.data.paramfiles3[1]))
            self.m_r2_3.SetValue(str(self.data.paramfiles3[2]))

        # The model-free models to use.
        if upload:
            # Loop over models m0 to m9.
            for i in range(10):
                # The object.
                obj = getattr(self, 'm%i' % i)

                # Upload to the store.
                self.data.model_toggle[i] = obj.GetValue()
        else:
            # Loop over models m0 to m9.
            for i in range(10):
                # The object.
                obj = getattr(self, 'm%i' % i)

                # Download from the store.
                obj.SetValue(self.data.model_toggle[i])

        # The structure file.
        if upload:
            self.data.structure_file = str(self.field_structure.GetValue())
        else:
            self.field_structure.SetValue(str(self.data.structure_file))

        # Unresolved residues.
        if upload:
            self.data.unresolved = str(self.field_unresolved.GetValue())
        else:
            self.field_unresolved.SetValue(str(self.data.unresolved))

        # The results directory.
        if upload:
            self.data.results_dir_model = str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str(self.data.results_dir_model))

        # Maximum iterations.
        if upload:
            self.data.max_iter = int(self.max_iter.GetValue())
        else:
            self.max_iter.SetValue(int(self.data.max_iter))
