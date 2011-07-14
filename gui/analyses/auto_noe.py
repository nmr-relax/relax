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
import time
import wx

# relax module imports.
from auto_analyses.noe import NOE_calc
from data import Relax_data_store; ds = Relax_data_store()
from relax_io import DummyFileObject
from status import Status; status = Status()

# relaxGUI module imports.
from gui.analyses.base import Base_frame
from gui.analyses.execute import Execute
from gui.analyses.results_analysis import color_code_noe
from gui.base_classes import Container
from gui.components.spectrum import Peak_intensity
from gui.controller import Redirect_text
from gui.derived_wx_classes import StructureTextCtrl
from gui.filedialog import opendir, openfile
from gui.message import error_message, missing_data
from gui.misc import add_border, gui_to_str, protected_exec, str_to_gui
from gui import paths
from gui.settings import load_sequence
from gui.user_functions.spectrum import Baseplane_rmsd_page, Integration_points_page, Read_intensities_page, Replicated_page
from gui.wizard import Wiz_window



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

        # Init.
        self.init_flag = True

        # New data container.
        if data_index == None:
            # First create the data pipe (if this fails, then no data is set up).
            if not protected_exec(self.gui.interpreter.pipe.create, pipe_name, 'noe'):
                self.init_flag = False
                return

            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add('NOE')

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].frq = ''
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

        # Register the method for updating the spin count for the completion of user functions.
        status.observers.uf_gui.register(self.data.pipe_name, self.update_spin_count)


    def assemble_data(self):
        """Assemble the data required for the Auto_noe class.

        See the docstring for auto_analyses.relax_fit for details.  All data is taken from the relax data store, so data upload from the GUI to there must have been previously performed.

        @return:    A container with all the data required for the auto-analysis, i.e. its keyword arguments seq_args, file_names, relax_times, int_method, mc_num.  Also a list of missing data types.
        @rtype:     class instance, list of str
        """

        # The data container.
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

        # Display the data pipe.
        self.add_text_sel_element(box, self.parent, text="The data pipe:", default=self.data.pipe_name, tooltip="This is the data pipe associated with this analysis.", editable=False)

        # Add the frequency selection GUI element.
        self.field_nmr_frq = self.add_text_sel_element(box, self.parent, text="NMR frequency label [MHz]", default=self.data.frq, tooltip="This label is added to the output files.  For example if the label is '600', the NOE values will be located in the file 'noe.600.out'.")

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self.parent, text="Results directory", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, fn=self.results_directory, button=True)

        # Add the spin GUI element.
        self.add_spin_systems(box, self.parent)

        # Add the peak list selection GUI element, with spacing.
        box.AddSpacer(10)
        self.peak_intensity = Peak_intensity(gui=self.gui, parent=self.parent, data=self.data, label="NOE", box=box, fn_add=self.peak_wizard)
        box.AddSpacer(10)

        # Add the execution GUI element.
        self.button_exec_id = self.add_execute_relax(box, self.execute)

        # Return the box.
        return box


    def delete(self):
        """Unregister the spin count from the user functions."""

        # Remove.
        status.observers.uf_gui.unregister(self.data.pipe_name)


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

        # Threading flag.
        thread = True
        if status.debug:
            thread = False

        # Start the thread.
        self.thread = Execute_noe(self.gui, data, self.data_index, thread=thread)
        self.thread.start()

        # Terminate the event.
        event.Skip()


    def launch_spin_editor(self, event):
        """The spin editor GUI element.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Show the molecule, residue, and spin tree window.
        self.gui.show_tree(None)


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


    def peak_wizard(self, event):
        """Launch the NOE peak loading wizard.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise a wizard.
        wizard = Wiz_window(size_x=1000, size_y=900, title="Set up the NOE peak intensities")

        # The spectrum.read_intensities page.
        page = Read_intensities_page(wizard, self.gui)
        wizard.add_page(page)

        # The spectrum.replicated page.
        page = Replicated_page(wizard, self.gui)
        wizard.add_page(page)

        # The spectrum.baseplane_rmsd page.
        page = Baseplane_rmsd_page(wizard, self.gui)
        wizard.add_page(page)

        # The spectrum.integration_points page.
        page = Integration_points_page(wizard, self.gui)
        wizard.add_page(page)

        # Run the wizard.
        wizard.run()


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



class Execute_noe(Execute):
    """The NOE analysis execution object."""

    def run_analysis(self):
        """Execute the calculation."""

        # Controller.
        if not status.debug and not status.test_mode:
            # Redirect relax output and errors to the controller.
            redir = Redirect_text(self.gui.controller)
            sys.stdout = redir
            sys.stderr = redir

        # Execute.
        NOE_calc(seq_args=self.data.seq_args, pipe_name=self.data.pipe_name, unresolved=self.data.unresolved, pdb_file=self.data.structure_file, output_file=self.data.filename, results_dir=self.data.save_dir, int_method='height', heteronuc=self.data.heteronuc, proton=self.data.proton, heteronuc_pdb='@N')

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
