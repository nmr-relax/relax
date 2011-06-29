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
"""Module containing the base class for the automatic R1 and R2 analysis frames."""

# Python module imports.
from os import sep
from string import replace
import sys
import thread
import time
import wx

# relax module imports.
from auto_analyses.relax_fit import Relax_fit
from data import Relax_data_store; ds = Relax_data_store()
from relax_io import DummyFileObject
from status import Status; status = Status()

# relaxGUI module imports.
from gui.analyses.base import Base_frame
from gui.base_classes import Container
from gui.components.spectrum import Peak_intensity
from gui.controller import Redirect_text, Thread_container
from gui.derived_wx_classes import StructureTextCtrl
from gui.filedialog import opendir
from gui.message import error_message, missing_data
from gui.misc import add_border
from gui import paths
from gui.settings import load_sequence



class Auto_rx(Base_frame):
    """The base class for the R1 and R2 frames."""

    # Hardcoded variables.
    analysis_type = None
    bitmap = None
    label = None

    def __init__(self, gui=None, notebook=None, analysis_name=None, pipe_name=None, data_index=None):
        """Build the automatic R1 and R2 analysis GUI frame elements.

        @keyword gui:           The main GUI class.
        @type gui:              gui.relax_gui.Main instance
        @keyword notebook:      The notebook to pack this frame into.
        @type notebook:         wx.Notebook instance
        @keyword analysis_name: The name of the analysis (the name in the tab part of the notebook).
        @type analysis_name:    str
        @keyword pipe_name:     The name of the data pipe associated with this analysis.
        @type pipe_name:        str
        @keyword data_index:    The index of the analysis in the relax data store (set to None if no data currently exists).
        @type data_index:       None or int
        """

        # Store the main class.
        self.gui = gui

        # New data container.
        if data_index == None:
            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add(self.label)

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].frq = ''
            ds.relax_gui.analyses[data_index].num = 0
            ds.relax_gui.analyses[data_index].file_list = []
            ds.relax_gui.analyses[data_index].ncyc = []
            ds.relax_gui.analyses[data_index].relax_times = []
            ds.relax_gui.analyses[data_index].save_dir = self.gui.launch_dir

        # Alias the data.
        self.data = ds.relax_gui.analyses[data_index]

        # The parent GUI element for this class.
        self.parent = wx.Panel(notebook, -1)

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.parent.SetSizer(box_main)

        # Build the central sizer, with borders.
        box_centre = add_border(box_main, border=self.border, packing=wx.HORIZONTAL)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        self.build_main_box(box_centre)


    def assemble_data(self):
        """Assemble the data required for the Relax_fit class.

        See the docstring for auto_analyses.relax_fit for details.  All data is taken from the relax data store, so data upload from the GUI to there must have been previously performed.

        @return:    A container with all the data required for the auto-analysis, i.e. its keyword arguments seq_args, file_names, relax_times, int_method, mc_num.  Also a flag stating if the data is complete and a list of missing data types.
        @rtype:     class instance, bool, list of str
        """

        # The data container.
        data = Container()
        complete = True
        missing = []

        # The pipe name.
        if hasattr(self.data, 'pipe_name'):
            data.pipe_name = self.data.pipe_name
        else:
            data.pipe_name = 'rx_%s' % time.asctime(time.localtime())

        # The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        if hasattr(self.data, 'sequence_file'):
            data.seq_args = [ds.relax_gui.sequencefile, None, None, 1, None, None, None, None]
        else:
            data.seq_args = None

        # The file names and relaxation times.
        for i in range(len(self.data.file_list)):
            # Hit the end of the list.
            if self.data.file_list[i] == '':
                break
        data.file_names = self.data.file_list[:i]
        data.relax_times = self.data.relax_times[:i]
        data.relax_times = [float(i) for i in data.relax_times]

        # Filename.
        self.filename = self.analysis_type + '.' + str(self.data.frq)

        # The integration method.
        data.int_method = 'height'

        # Import golbal settings.
        global_settings = ds.relax_gui.global_setting

        # Hetero nucleus name.
        data.heteronuc = global_settings[2]

        # Spin id of the heteronucleus.
        data.load_spin_ids = '@' + global_settings[2]

        # Proton name.
        data.proton = global_settings[3]

        # Increment size.
        data.inc = int(global_settings[4])

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        data.mc_num = int(global_settings[6])

        # Unresolved residues
        file = DummyFileObject()
        entries = self.data.unresolved
        entries = replace(entries, ',', '\n')
        file.write(entries)
        file.close()
        data.unresolved = file

        # Structure file.
        if self.data.structure_file == self.gui.structure_file_pdb_msg:
            data.structure_file = None
        else:
            data.structure_file = self.data.structure_file

        # Set Structure file as None if a structure file is loaded.
        if data.structure_file == '!!! Sequence file selected !!!':
            data.structure_file = None

        # Results directory.
        data.save_dir = self.data.save_dir

        # No sequence data.
        if not data.seq_args and not data.structure_file:
            complete = False
            missing.append('Sequence data files (text or PDB)')

        # Return the container, flag, and list of missing data.
        return data, complete, missing


    def build_right_box(self):
        """Construct the right hand box to pack into the main Rx box.

        @return:    The right hand box element containing all Rx GUI elements (excluding the bitmap) to pack into the main Rx box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_title(box, "Setup for %s relaxation analysis" % self.label)

        # Add the frequency selection GUI element.
        self.field_nmr_frq = self.add_text_sel_element(box, self.parent, text="NMR Frequency [MHz]", default=str(self.data.frq))

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self.parent, text="Results directory", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, fn=self.results_directory, button=True)

        # Add the sequence file selection GUI element.
        self.field_sequence = self.add_text_sel_element(box, self.parent, text="Sequence file", default=str(self.gui.sequence_file_msg), fn=self.load_sequence, editable=False, button=True)

        # Add the structure file selection GUI element.
        self.field_structure = self.add_text_sel_element(box, self.parent, text="Sequence from PDB structure file", default=self.gui.structure_file_pdb_msg, control=StructureTextCtrl, fn='open_file', editable=False, button=True)

        # Add the unresolved spins GUI element.
        self.field_unresolved = self.add_text_sel_element(box, self.parent, text="Unresolved residues")

        # Add the peak list selection GUI element, with spacing.
        box.AddSpacer(10)
        self.peak_intensity = Peak_intensity(gui=self.gui, parent=self.parent, subparent=self, data=self.data, label=self.label, box=box)
        box.AddSpacer(10)

        # Add the execution GUI element.
        self.button_exec_id = self.add_execute_relax(box, self.execute)

        # Return the box.
        return box


    def execute(self, event):
        """Set up, execute, and process the automatic Rx analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # relax execution lock.
        status = Status()
        if status.exec_lock.locked():
            error_message("relax is currently executing.", "relax execution lock")
            return

        # Synchronise the frame data to the relax data store.
        self.sync_ds(upload=True)

        # Assemble all the data needed for the Relax_fit class.
        data, missing = self.assemble_data()

        # Missing data.
        if len(missing):
            missing_data(missing)
            return

        # Display the relax controller.
        if not status.debug:
            self.gui.controller.Show()

        # Start the thread.
        if status.debug:
            self.execute_thread('dummy')
        else:
            id = thread.start_new_thread(self.execute_thread, ('dummy',))


    def execute_thread(self, dummy_string):
        """Execute the calculation in a thread."""

        # Controller.
        if not status.debug:
            # Redirect relax output and errors to the controller.
            redir = Redirect_text(self.gui.controller)
            sys.stdout = redir
            sys.stderr = redir

            # Print a header in the controller.
            header = 'Starting %s calculation' % self.label
            underline = '-' * len(header)
            wx.CallAfter(self.gui.controller.log_panel.AppendText, (header+'\n\n'))
            time.sleep(0.5)

        # Execute.
        Relax_fit(file_root=self.filename, pipe_name=data.pipe_name, seq_args=data.seq_args, results_directory=data.save_dir, file_names=data.file_names, relax_times=data.relax_times, int_method=data.int_method, mc_num=data.mc_num, pdb_file=data.structure_file, unresolved=data.unresolved, view_plots = False, heteronuc=data.heteronuc, proton=data.proton, load_spin_ids=data.load_spin_ids, inc=data.inc)

        # Feedback about success.
        if not status.debug:
            wx.CallAfter(self.gui.controller.log_panel.AppendText, '\n\n__________________________________________________________\n\nSuccessfully calculated Rx values\n__________________________________________________________')

        # Add noe grace plot to results list.
        self.gui.list_rx.Append(data.save_dir+sep+'grace'+sep+self.filename+'.agr')
        self.gui.list_rx.Append(data.save_dir+sep+'grace'+sep+'intensities_norm.agr')

        # Add noe grace plot to relax data store.
        ds.relax_gui.results_rx.append(data.save_dir+sep+'grace'+sep+self.filename+'.agr')
        ds.relax_gui.results_rx.append(data.save_dir+sep+'grace'+sep+'intensities_norm.agr')


    def load_sequence(self, event):
        """The sequence loading GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Select the file.
        file = load_sequence()

        # Nothing selected.
        if file == None:
            return

        # Store the file.
        self.data.sequence_file = file

        # Sync.
        self.sync_ds(upload=False)


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


    def sync_ds(self, upload=False):
        """Synchronise the rx analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The frequency.
        if upload:
            self.data.frq = str(self.field_nmr_frq.GetValue())
        elif hasattr(self.data, 'frq'):
            self.field_nmr_frq.SetValue(str(self.data.frq))

        # The results directory.
        if upload:
            self.data.save_dir = str(self.field_results_dir.GetValue())
        elif hasattr(self.data, 'save_dir'):
            self.field_results_dir.SetValue(str(self.data.save_dir))

        # The sequence file.
        if upload:
            file = str(self.field_sequence.GetValue())
            if file != self.gui.sequence_file_msg:
                self.data.sequence_file = str(self.field_sequence.GetValue())
        elif hasattr(self.data, 'sequence_file'):
            self.field_sequence.SetValue(str(self.data.sequence_file))

        # The structure file.
        if upload:
            self.data.structure_file = str(self.field_structure.GetValue())
        elif hasattr(self.data, 'structure_file'):
            self.field_structure.SetValue(str(self.data.structure_file))

        # Unresolved residues.
        if upload:
            self.data.unresolved = str(self.field_unresolved.GetValue())
        elif hasattr(self.data, 'unresolved'):
            self.field_unresolved.SetValue(str(self.data.unresolved))

        # The peak lists and relaxation times.
        self.peak_intensity.sync_ds(upload)
