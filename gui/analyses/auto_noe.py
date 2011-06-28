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
"""Module containing the base class for the automatic NOE analysis frames."""

# Python module imports.
from os import sep
from os.path import dirname
from string import replace
import sys
from threading import Thread
import time
import wx

# relax module imports.
from auto_analyses.noe import NOE_calc
from data import Relax_data_store; ds = Relax_data_store()
from relax_io import DummyFileObject
from status import Status; status = Status()

# relaxGUI module imports.
from gui.analyses.base import Base_frame
from gui.analyses.results_analysis import color_code_noe
from gui.base_classes import Container
from gui.controller import Redirect_text, Thread_container
from gui.derived_wx_classes import StructureTextCtrl
from gui.filedialog import opendir, openfile
from gui.message import error_message, missing_data
from gui.misc import add_border, gui_to_str, str_to_gui
from gui import paths
from gui.settings import load_sequence



class Auto_noe(Base_frame):
    """The base class for the noe frames."""

    # Hardcoded variables.
    analysis_type = None
    bitmap = [paths.ANALYSIS_IMAGE_PATH+"noe_200x200.png",
              paths.IMAGE_PATH+'noe.png']
    label = None

    def __init__(self, gui=None, notebook=None, analysis_name=None, pipe_name=None, data_index=None):
        """Build the automatic NOE analysis GUI frame elements.

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
            data_index = ds.relax_gui.analyses.add('NOE')

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].frq = ''
            ds.relax_gui.analyses[data_index].ref_file = ''
            ds.relax_gui.analyses[data_index].sat_file = ''
            ds.relax_gui.analyses[data_index].ref_rmsd = 1000
            ds.relax_gui.analyses[data_index].sat_rmsd = 1000
            ds.relax_gui.analyses[data_index].save_dir = self.gui.launch_dir
            ds.relax_gui.analyses[data_index].results_list = []

        # Alias the data.
        self.data = ds.relax_gui.analyses[data_index]
        self.data_index = data_index

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
        """Assemble the data required for the Auto_noe class.

        See the docstring for auto_analyses.relax_fit for details.  All data is taken from the relax data store, so data upload from the GUI to there must have been previously performed.

        @return:    A container with all the data required for the auto-analysis, i.e. its keyword arguments seq_args, file_names, relax_times, int_method, mc_num.  Also a list of missing data types.
        @rtype:     class instance, bool, list of str
        """

        # The data container and flag.
        data = Container()
        missing = []

        # The pipe name.
        if hasattr(self.data, 'pipe_name'):
            data.pipe_name = self.data.pipe_name
        else:
            data.pipe_name = 'noe_%s' % time.asctime(time.localtime())

        # The sequence data (file name, dir, mol_name_col, res_num_col, res_name_col, spin_num_col, spin_name_col, sep).  These are the arguments to the  sequence.read() user function, for more information please see the documentation for that function.
        if hasattr(self.data, 'sequence_file'):
            data.seq_args = [self.data.sequence_file, None, None, 1, None, None, None, None]
        else:
            data.seq_args = None

        # The frequency.
        frq = gui_to_str(self.field_nmr_frq.GetValue())
        if frq == None:
            missing.append('NMR frequency')

        # Filename.
        data.filename = 'noe.%s.out' % frq

        # Saturated peak list and background noe.
        data.sat_file = self.data.sat_file
        if not data.sat_file:
            missing.append('Saturated peak list')
        data.sat_rmsd = int(self.data.sat_rmsd)

        # Reference peak list and background noe.
        data.ref_file = self.data.ref_file
        if not data.ref_file:
            missing.append('Reference peak list')
        data.ref_rmsd = int(self.data.ref_rmsd)

        # Results directory.
        data.save_dir = self.data.save_dir

        # The integration method.
        data.int_method = 'height'

        # Import global settings.
        global_settings = ds.relax_gui.global_setting

        # Hetero nucleus name.
        data.heteronuc = global_settings[2]

        # Proton name.
        data.proton = global_settings[3]

        # Unresolved spins.
        file = DummyFileObject()
        if self.data.unresolved:
            entries = self.data.unresolved
            entries = replace(entries, ',', '\n')
            file.write(entries)
        file.close()
        data.unresolved = file

        # Structure file.
        if hasattr(self.data, 'structure_file') and self.data.structure_file != self.gui.structure_file_pdb_msg:
            data.structure_file = self.data.structure_file
        else:
            data.structure_file = None

        # Set Structure file as None if a sequence file is loaded.
        if data.structure_file == '!!! Sequence file selected !!!':
            data.structure_file = None

        # No sequence data.
        if not data.seq_args and not data.structure_file:
            missing.append('Sequence data files (text or PDB)')

        # Return the container and list of missing data.
        return data, missing


    def build_right_box(self):
        """Construct the right hand box to pack into the main NOE box.

        @return:    The right hand box element containing all NOE GUI elements (excluding the bitmap) to pack into the main Rx box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_title(box, "Setup for steady-state NOE analysis")

        # Add the frequency selection GUI element.
        self.field_nmr_frq = self.add_text_sel_element(box, self.parent, text="NMR Frequency [MHz]", default=str_to_gui(self.data.frq))

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self.parent, text="Results directory", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, fn=self.results_directory, button=True)

        # Add the sequence file selection GUI element.
        self.field_sequence = self.add_text_sel_element(box, self.parent, text="Sequence file", default=str_to_gui(self.gui.sequence_file_msg), fn=self.load_sequence, editable=False, button=True)

        # Add the structure file selection GUI element.
        self.field_structure = self.add_text_sel_element(box, self.parent, text="Sequence from PDB structure file", default=self.gui.structure_file_pdb_msg, control=StructureTextCtrl, fn='open_file', editable=False, button=True)

        # Add the unresolved spins GUI element.
        self.field_unresolved = self.add_text_sel_element(box, self.parent, text="Unresolved residues")

        # Add peak list selection header.
        self.add_subtitle(box, "NOE peak lists")

        # Add the saturated NOE peak list selection GUI element.
        self.field_sat_noe = self.add_text_sel_element(box, self.parent, text="Saturated NOE peak list", default=self.data.sat_file, fn=self.sat_file, button=True)

        # Add the saturated RMSD background GUI element:
        self.field_sat_rmsd = self.add_text_sel_element(box, self.parent, text="Baseplane RMSD", default=str_to_gui(self.data.sat_rmsd))

        # Add the reference NOE peak list selection GUI element.
        self.field_ref_noe = self.add_text_sel_element(box, self.parent, text="Reference NOE peak list", default=self.data.ref_file, fn=self.ref_file, button=True)

        # Add the reference RMSD background GUI element:
        self.field_ref_rmsd = self.add_text_sel_element(box, self.parent, text="Baseplane RMSD", default=str_to_gui(self.data.ref_rmsd))

        # Add a stretchable spacer.
        box.AddStretchSpacer()

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
            event.Skip()
            return

        # Synchronise the frame data to the relax data store.
        self.sync_ds(upload=True)

        # Assemble all the data needed for the auto-analysis.
        data, missing = self.assemble_data()

        # Missing data.
        if len(missing):
            missing_data(missing)
            return

        # Display the relax controller (if not debugging).
        if not status.debug:
            self.gui.controller.Show()

        # Start the thread (if not debugging).
        if status.debug:
            self.thread = Execute(self.gui, data, self.data_index)
        else:
            self.thread = Execute_thread(self.gui, data, self.data_index)
            self.thread.start()

        # Terminate the event.
        event.Skip()


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
        self.field_sequence.SetValue(str_to_gui(file))

        # Terminate the event.
        event.Skip()


    def ref_file(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original directory.
        backup = gui_to_str(self.field_ref_noe.GetValue())

        # The directory.
        directory = None
        if backup != None:
            directory = dirname(backup)

        # Select the file.
        self.data.ref_file = openfile('Select reference NOE peak list', directory=directory, default = 'all files (*.*)|*')

        # Restore the backup file if no file was chosen.
        if not self.data.ref_file:
            self.data.ref_file = backup

        # Place the path in the text box.
        self.field_ref_noe.SetValue(self.data.ref_file)

        # Terminate the event.
        event.Skip()


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


    def sat_file(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Store the original directory.
        backup = gui_to_str(self.field_sat_noe.GetValue())

        # The directory.
        directory = None
        if backup != None:
            directory = dirname(backup)

        # Select the file.
        self.data.sat_file = openfile('Select saturated NOE peak list', directory=directory, default = 'all files (*.*)|*')

        # Restore the backup file if no file was chosen.
        if not self.data.sat_file:
            self.data.sat_file = backup

        # Place the path in the text box.
        self.field_sat_noe.SetValue(self.data.sat_file)

        # Terminate the event.
        event.Skip()


    def sync_ds(self, upload=False):
        """Synchronise the noe analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The frequency.
        if upload:
            self.data.frq = gui_to_str(self.field_nmr_frq.GetValue())
        else:
            self.field_nmr_frq.SetValue(str_to_gui(self.data.frq))

        # The results directory.
        if upload:
            self.data.save_dir = gui_to_str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str_to_gui(self.data.save_dir))

        # The sequence file.
        if upload:
            file = gui_to_str(self.field_sequence.GetValue())
            if file != self.gui.sequence_file_msg:
                self.data.sequence_file = gui_to_str(self.field_sequence.GetValue())
        elif hasattr(self.data, 'sequence_file'):
            self.field_sequence.SetValue(str_to_gui(self.data.sequence_file))

        # The structure file.
        if upload:
            file = gui_to_str(self.field_structure.GetValue())
            if file != self.gui.structure_file_pdb_msg:
                self.data.structure_file = gui_to_str(self.field_structure.GetValue())
        elif hasattr(self.data, 'structure_file'):
            self.field_structure.SetValue(str_to_gui(self.data.structure_file))

        # Unresolved residues.
        if upload:
            self.data.unresolved = gui_to_str(self.field_unresolved.GetValue())
        elif hasattr(self.data, 'unresolved'):
            self.field_unresolved.SetValue(str_to_gui(self.data.unresolved))

        # Reference peak file.
        if upload:
            self.data.ref_file = gui_to_str(self.field_ref_noe.GetValue())
        elif hasattr(self.data, 'ref_file'):
            self.field_ref_noe.SetValue(str_to_gui(self.data.ref_file))

        # Reference rmsd.
        if upload:
            self.data.ref_rmsd = gui_to_str(self.field_ref_rmsd.GetValue())
        elif hasattr(self.data, 'ref_rmsd'):
            self.field_ref_rmsd.SetValue(str_to_gui(self.data.ref_rmsd))

        # Saturated peak file.
        if upload:
            self.data.sat_file = gui_to_str(self.field_sat_noe.GetValue())
        elif hasattr(self.data, 'sat_file'):
            self.field_sat_noe.SetValue(str_to_gui(self.data.sat_file))

        # Saturated rmsd.
        if upload:
            self.data.sat_rmsd = gui_to_str(self.field_sat_rmsd.GetValue())
        elif hasattr(self.data, 'sat_rmsd'):
            self.field_sat_rmsd.SetValue(str_to_gui(self.data.sat_rmsd))



class Execute:
    """The NOE analysis execution object."""

    def __init__(self, gui, data, data_index):
        """Set up the NOE analysis execution object.

        @param gui:         The GUI object.
        @type gui:          wx object
        @param data:        The data container with all data for the analysis.
        @type data:         class instance
        @param data_index:  The index of the analysis in the relax data store.
        @type data_index:   int
        """

        # Store the args.
        self.gui = gui
        self.data = data
        self.data_index = data_index

        # Execute.
        self.run()


    def run(self):
        """Execute the calculation."""

        # Controller.
        if not status.debug:
            # Redirect relax output and errors to the controller.
            redir = Redirect_text(self.gui.controller)
            sys.stdout = redir
            sys.stderr = redir

        # Execute.
        NOE_calc(seq_args=self.data.seq_args, pipe_name=self.data.pipe_name, noe_ref=self.data.ref_file, noe_ref_rmsd=self.data.ref_rmsd, noe_sat=self.data.sat_file, noe_sat_rmsd=self.data.sat_rmsd, unresolved=self.data.unresolved, pdb_file=self.data.structure_file, output_file=self.data.filename, results_dir=self.data.save_dir, int_method='height', heteronuc=self.data.heteronuc, proton=self.data.proton, heteronuc_pdb='@N')

        # Alias the relax data store data.
        data = ds.relax_gui.analyses[self.data_index]

        # Is there a results list (old results file support)?
        if not hasattr(data, 'results_list'):
            data.results_list = []

        # Add the NOE grace plot to the results list.
        data.results_list.append(data.save_dir+sep+'grace'+sep+'noe.agr')

        # Create a PyMOL macro, if a structure exists.
        if hasattr(data, 'structure_file'):
            # The macro.
            color_code_noe(data.save_dir, data.structure_file)

            # Add the macro to the results list.
            data.results_list.append(data.save_dir+sep+'noe.pml')



class Execute_thread(Execute, Thread):
    """The NOE analysis thread execution object."""

    def __init__(self, gui, data):
        """Set up the NOE analysis thread execution object.

        @param gui:         The GUI object.
        @type gui:          wx object
        @param data:        The data container with all data for the analysis.
        @type data:         class instance
        @param data_index:  The index of the analysis in the relax data store.
        @type data_index:   int
        """

        # Store the args.
        self.gui = gui
        self.data = data
        self.data_index = data_index

        # Set up the thread object.
        Thread.__init__(self)
