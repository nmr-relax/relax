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
"""Module containing the base class for the automatic R1 and R2 analysis frames."""

# Python module imports.
from os import sep
import sys
import thread
import time
import wx

# relax module imports.
from auto_analyses.noe import NOE_calc
from data import Relax_data_store; ds = Relax_data_store()

# relaxGUI module imports.
from gui_bieri.analyses.project import open_file
from gui_bieri.base_classes import Container
from gui_bieri.controller import Redirect_text, Thread_container
from gui_bieri.derived_wx_classes import StructureTextCtrl
from gui_bieri.filedialog import multi_openfile, opendir, openfile
from gui_bieri.message import error_message
from gui_bieri.paths import IMAGE_PATH



class Auto_noe:
    """The base class for the noe frames."""

    # Hardcoded variables.
    analysis_type = None
    bitmap = None
    label = None

    def __init__(self, gui, notebook, hardcoded_index=None):
        """Build the automatic NOE analysis GUI frame elements.

        @param gui:                 The main GUI class.
        @type gui:                  gui_bieri.relax_gui.Main instance
        @param notebook:            The notebook to pack this frame into.
        @type notebook:             wx.Notebook instance
        @keyword hardcoded_index:   Kludge for the current GUI layout.
        @type hardcoded_index:      int
        """

        # Store the main class.
        self.gui = gui

        # Alias the storage container in the relax data store.
        self.data = ds.relax_gui.analyses[hardcoded_index]

        # The parent GUI element for this class.
        self.parent = wx.Panel(notebook, -1)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        main_box = self.build_main_box()
        self.parent.SetSizer(main_box)

        # Set the frame font size.
        self.parent.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, ""))


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
        sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.BitmapButton(self.parent, -1, wx.Bitmap(IMAGE_PATH+'relax_start.gif', wx.BITMAP_TYPE_ANY))
        button.SetName('hello')
        button.SetSize(button.GetBestSize())
        self.gui.Bind(wx.EVT_BUTTON, self.execute, button)
        sizer.Add(button, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALIGN_RIGHT, 0)


    def add_frame_title(self, box):
        """Create and add the frame title to the given box.

        @param box:     The box element to pack the frame title into.
        @type box:      wx.BoxSizer instance
        """

        # The title.
        label = wx.StaticText(self.parent, -1, "Set-up for %s relaxation analysis:" % self.label)

        # The font properties.
        label.SetFont(wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))

        # Pack the title.
        box.Add(label, 0, wx.BOTTOM|wx.ADJUST_MINSIZE, 18)


    def add_frq(self, box):
        """Create and add the frequency selection GUI element to the given box.

        @param box:     The box element to pack the PDB file selection GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "NMR Frequency [MHz]:", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_nmr_frq = wx.TextCtrl(self.parent, -1, str(self.data.frq))
        self.field_nmr_frq.SetMinSize((350, 27))
        sizer.Add(self.field_nmr_frq, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def add_results_dir(self, box):
        """Create and add the results directory GUI element to the given box.

        @param box:     The box element to pack the results directory GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Results directory", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_results_dir = wx.TextCtrl(self.parent, -1, self.data.save_dir)
        self.field_results_dir.SetMinSize((350, 27))
        sizer.Add(self.field_results_dir, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.Button(self.parent, -1, "Change")
        button.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.results_directory, button)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)

        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def add_structure_selection(self, box):
        """Create and add the structure file selection GUI element to the given box.

        @param box:     The box element to pack the structure file selection GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Structure file (.pdb)", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_structure = StructureTextCtrl(self.parent, -1, self.gui.structure_file_pdb_msg)
        self.field_structure.SetEditable(False)
        self.field_structure.SetMinSize((350, 27))
        sizer.Add(self.field_structure, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The button.
        button = wx.Button(self.parent, -1, "Change")
        button.SetMinSize((103, 27))
        self.gui.Bind(wx.EVT_BUTTON, self.field_structure.open_file, button)
        sizer.Add(button, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 10)

        # Add the element to the box.
        box.Add(sizer, 1, wx.EXPAND, 0)


    def add_unresolved_spins(self, box):
        """Create and add the unresolved spins GUI element to the given box.

        @param box:     The box element to pack the unresolved spins GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The label.
        label = wx.StaticText(self.parent, -1, "Unresolved residues:", style=wx.ALIGN_RIGHT)
        label.SetMinSize((230, 17))
        sizer.Add(label, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)

        # The text input field.
        self.field_unresolved = wx.TextCtrl(self.parent, -1, "")
        self.field_unresolved.SetMinSize((350, 27))
        sizer.Add(self.field_unresolved, 0, wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 0)
        
        # Add the element to the box.
        box.Add(sizer, 0, wx.EXPAND|wx.SHAPED, 0)


    def assemble_data(self):
        """Assemble the data required for the Relax_fit class.

        See the docstring for auto_analyses.relax_fit for details.  All data is taken from the relax data store, so data upload from the GUI to there must have been previously performed.

        @return:    A container with all the data required for Relax_fit, i.e. its keyword arguments seq_args, file_names, relax_times, int_method, mc_num.
        @rtype:     class instance
        """

        # The data container.
        data = Container()

        # The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        data.seq_args = ['fixme!', None, None, 2, 3, 4, 5, None]

        # The file names and relaxation times.
        for i in range(len(self.data.file_list)):
            # Hit the end of the list.
            if self.data.file_list[i] == '':
                break
        data.file_names = self.data.file_list[:i]
        data.relax_times = self.data.relax_times[:i]

        # The integration method.
        data.int_method = 'height'

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        data.mc_num = 500

        # Unresolved resiudes
        data.unresolved = self.data.unresolved

        # Structure File
        data.structure_file = self.data.structure_file

        # Return the container.
        return data


    def build_main_box(self):
        """Construct the highest level box to pack into the automatic Rx analysis frame.

        @return:    The main box element containing all Rx GUI elements to pack directly into the automatic Rx analysis frame.
        @rtype:     wx.BoxSizer instance
        """

        # Use a horizontal packing of elements.
        box = wx.BoxSizer(wx.HORIZONTAL)

        # Add the model-free bitmap picture.
        self.bitmap_1_copy_copy = wx.StaticBitmap(self.parent, -1, wx.Bitmap(self.bitmap, wx.BITMAP_TYPE_ANY))
        box.Add(self.bitmap_1_copy_copy, 0, wx.ADJUST_MINSIZE, 10)

        # Build the right hand box and pack it next to the bitmap.
        right_box = self.build_right_box()
        box.Add(right_box, 0, 0, 0)

        # Return the box.
        return box


    def build_right_box(self):
        """Construct the right hand box to pack into the main Rx box.

        @return:    The right hand box element containing all Rx GUI elements (excluding the bitmap) to pack into the main Rx box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_frame_title(box)

        # Add the frequency selection GUI element.
        self.add_frq(box)

        # Add the results directory GUI element.
        self.add_results_dir(box)

        # Add the structure file selection GUI element.
        self.add_structure_selection(box)

        # Add the unresolved spins GUI element.
        self.add_unresolved_spins(box)

        # Add the execution GUI element.
        self.add_execute_relax(box)

        # Return the box.
        return box


    def execute(self, event):
        """Set up, execute, and process the automatic Rx analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Synchronise the frame data to the relax data store.
        self.sync_ds(upload=True)

        # Display the relax controller.
        self.gui.controller.Show()

        # FIXME:  Debugging code, non-threaded exec.
        self.execute_thread()
        event.Skip()
        return

        # The thread object storage.
        self.gui.calc_threads.append(Thread_container())
        thread_cont = self.gui.calc_threads[-1]

        # Start the thread.
        id = thread.start_new_thread(self.execute_thread, ())

        # Add the thread info to the container.
        thread_cont.id = id
        thread_cont.analysis_type = self.analysis_type

        # Terminate the event.
        event.Skip()


    def execute_thread(self):
        """Execute the calculation in a thread."""

        # Redirect relax output and errors to the controller.
        redir = Redirect_text(self.gui.controller)
        sys.stdout = redir
        sys.stderr = redir

        # Print a header in the controller.
        header = 'Starting %s calculation' % self.label
        underline = '-' * len(header)
        wx.CallAfter(self.gui.controller.log_panel.AppendText, (header+'\n\n'))
        time.sleep(0.5)

        # Assemble all the data needed for the Relax_fit class.
        data = self.assemble_data()

        # Execute.
        Relax_fit(seq_args=data.seq_args, file_names=data.file_names, relax_times=data.relax_times, int_method=data.int_method, mc_num=data.mc_num, pdb_file = data.structure_file, unresolved = data.unresolved)


    def link_data(self, data):
        """Re-alias the storage container in the relax data store.
        @keyword data:      The data storage container.
        @type data:         class instance
        """

        # Re-alias.
        self.data = data

        # Re-alias in the peak intensity object as well.
        self.peak_intensity.data = data


    def results_directory(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original directory.
        backup = self.field_results_dir.GetValue()

        # Select the file.
        self.data.save_dir = opendir('Select results directory', default=self.field_results_dir.GetValue())

        # Restore the backup file if no file was chosen.
        if not self.data.save_dir:
            self.data.save_dir = backup

        # Place the path in the text box.
        self.field_results_dir.SetValue(self.data.save_dir)

        # Terminate the event.
        event.Skip()


    def sync_ds(self, upload=False):
        """Synchronise the rx analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The frequency.
        if upload:
            self.data.frq = str(self.field_nmr_frq.GetValue())
        else:
            self.field_nmr_frq.SetValue(str(self.data.frq))

        # The results directory.
        if upload:
            self.data.save_dir = str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str(self.data.save_dir))

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

        # The peak lists and relaxation times.
        self.peak_intensity.sync_ds(upload)
