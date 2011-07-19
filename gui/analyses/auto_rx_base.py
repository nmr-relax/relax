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
from string import lower
import sys
import wx

# relax module imports.
from auto_analyses.relax_fit import Relax_fit
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.mol_res_spin import are_spins_named
from status import Status; status = Status()

# relaxGUI module imports.
from gui.analyses.base import Base_frame, Spectral_error_type_page
from gui.analyses.execute import Execute
from gui.base_classes import Container
from gui.components.spectrum import Spectra_list
from gui.controller import Redirect_text
from gui.filedialog import opendir
from gui.message import error_message, missing_data
from gui.misc import add_border, gui_to_int, gui_to_str, int_to_gui, protected_exec, str_to_gui
from gui import paths
from gui.user_functions.relax_fit import Relax_time_page
from gui.user_functions.spectrum import Baseplane_rmsd_page, Integration_points_page, Read_intensities_page, Replicated_page
from gui.wizard import Wiz_window



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

        # Init.
        self.init_flag = True

        # New data container.
        if data_index == None:
            # First create the data pipe (if this fails, then no data is set up).
            if not protected_exec(self.gui.interpreter.pipe.create, pipe_name, 'relax_fit'):
                self.init_flag = False
                return

            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add(self.label)

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].frq = ''
            ds.relax_gui.analyses[data_index].grid_inc = None
            ds.relax_gui.analyses[data_index].mc_sim_num = None
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
        """Assemble the data required for the Relax_fit class.

        @return:    A container with all the data required for the auto-analysis.
        @rtype:     class instance, list of str
        """

        # The data container.
        data = Container()
        missing = []

        # The pipe name.
        data.pipe_name = self.data.pipe_name

        # The frequency.
        frq = gui_to_str(self.field_nmr_frq.GetValue())
        if frq == None:
            missing.append('NMR frequency')

        # File root.
        data.file_root = '%s.%s' % (self.analysis_type, frq)

        # Increment size.
        data.inc = gui_to_int(self.grid_inc.GetValue())

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        data.mc_sim_num = gui_to_int(self.mc_sim_num.GetValue())

        # Results directory.
        data.save_dir = self.data.save_dir

        # Return the container and list of missing data.
        return data, missing


    def build_right_box(self):
        """Construct the right hand box to pack into the main Rx box.

        @return:    The right hand box element containing all Rx GUI elements (excluding the bitmap) to pack into the main Rx box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_title(box, "Setup for %s relaxation analysis" % self.label)

        # Display the data pipe.
        self.add_text_sel_element(box, self.parent, text="The data pipe:", default=self.data.pipe_name, tooltip="This is the data pipe associated with this analysis.", editable=False)

        # Add the frequency selection GUI element.
        self.field_nmr_frq = self.add_text_sel_element(box, self.parent, text="NMR frequency label [MHz]", default=self.data.frq, tooltip="This label is added to the output files.  For example if the label is '600', the %s values will be located in the file '%s.600.out'." % (self.label, lower(self.label)))

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self.parent, text="Results directory", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, fn=self.results_directory, button=True)

        # Add the spin GUI element.
        self.add_spin_systems(box, self.parent)

        # Add the peak list selection GUI element, with spacing.
        box.AddSpacer(10)
        self.peak_intensity = Spectra_list(gui=self.gui, parent=self.parent, box=box, id=str(self.data_index), fn_add=self.peak_wizard)
        box.AddSpacer(10)

        # The optimisation settings.
        self.grid_inc = self.add_spin_element(box, self.parent, text="Grid search increments:", default=11, min=1, max=100, tooltip="This is the number of increments per dimension of the grid search performed prior to numerical optimisation.")
        self.mc_sim_num = self.add_spin_element(box, self.parent, text="Monte Carlo simulation number:", default=500, min=1, max=100000, tooltip="This is the number of Monte Carlo simulations performed for error propagation and analysis.")

        # Some spacing.
        box.AddSpacer(10)

        # Add the execution GUI element.
        self.button_exec_id = self.add_execute_relax(box, self.execute)

        # Return the box.
        return box


    def delete(self):
        """Unregister the spin count from the user functions."""

        # Clean up the peak intensity object.
        self.peak_intensity.delete()

        # Remove.
        status.observers.uf_gui.unregister(self.data.pipe_name)


    def execute(self, event):
        """Set up, execute, and process the automatic Rx analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # relax execution lock.
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
        if not status.debug and status.show_gui:
            self.gui.controller.Show()

        # Threading flag.
        thread = True
        if status.debug:
            thread = False

        # Start the thread.
        self.thread = Execute_rx(self.gui, data, self.data_index, thread=thread)
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


    def peak_wizard(self, event):
        """Launch the NOE peak loading wizard.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Change the cursor to busy.
        wx.BeginBusyCursor()

        # First check that at least a single spin is named!
        if not are_spins_named():
            error_message("No spins have been named.  Please use the spin.name user function first, otherwise it is unlikely that any data will be loaded from the peak intensity file.\n\nThis message can be ignored if the generic file format is used and spin names have not been specified.", caption='Incomplete setup')

        # Initialise a wizard.
        self.wizard = Wiz_window(size_x=1000, size_y=900, title="Set up the %s peak intensities" % self.label)
        self.page_indices = {}

        # The spectrum.read_intensities page.
        self.page_intensity = Read_intensities_page(self.wizard, self.gui)
        self.page_indices['read'] = self.wizard.add_page(self.page_intensity, skip_button=True, proceed_on_error=False)

        # Error type selection page.
        self.page_error_type = Spectral_error_type_page(self.wizard, self.gui)
        self.page_indices['err_type'] = self.wizard.add_page(self.page_error_type, apply_button=False)
        self.wizard.set_seq_next_fn(self.page_indices['err_type'], self.wizard_page_after_error_type)

        # The spectrum.replicated page.
        page = Replicated_page(self.wizard, self.gui)
        self.page_indices['repl'] = self.wizard.add_page(page, skip_button=True)
        self.wizard.set_seq_next_fn(self.page_indices['repl'], self.wizard_page_after_repl)
        page.on_display_post = self.wizard_update_repl

        # The spectrum.baseplane_rmsd page.
        page = Baseplane_rmsd_page(self.wizard, self.gui)
        self.page_indices['rmsd'] = self.wizard.add_page(page, skip_button=True)
        self.wizard.set_seq_next_fn(self.page_indices['rmsd'], self.wizard_page_after_rmsd)
        page.on_display_post = self.wizard_update_rmsd

        # The spectrum.integration_points page.
        page = Integration_points_page(self.wizard, self.gui)
        self.page_indices['pts'] = self.wizard.add_page(page, skip_button=True)
        page.on_display_post = self.wizard_update_pts

        # The relax_fit.relax_time page.
        page = Relax_time_page(self.wizard, self.gui)
        self.page_indices['relax_time'] = self.wizard.add_page(page, skip_button=False)
        page.on_display_post = self.wizard_update_relax_time

        # Reset the cursor.
        wx.EndBusyCursor()

        # Run the wizard.
        self.wizard.run()


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
            self.data.frq = gui_to_str(self.field_nmr_frq.GetValue())
        else:
            self.field_nmr_frq.SetValue(str_to_gui(self.data.frq))

        # The grid incs.
        if upload:
            self.data.grid_inc = gui_to_int(self.grid_inc.GetValue())
        elif hasattr(self.data, 'grid_inc'):
            self.grid_inc.SetValue(int(self.data.grid_inc))

        # The MC sim number.
        if upload:
            self.data.mc_sim_num = gui_to_int(self.mc_sim_num.GetValue())
        elif hasattr(self.data, 'mc_sim_num'):
            self.mc_sim_num.SetValue(int(self.data.mc_sim_num))

        # The results directory.
        if upload:
            self.data.save_dir = gui_to_str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str_to_gui(self.data.save_dir))


    def wizard_page_after_error_type(self):
        """Set the page after the error type choice.

        @return:    The index of the next page, which is the current page index plus one.
        @rtype:     int
        """

        # Go to the spectrum.baseplane_rmsd page.
        if self.page_error_type.selection == 'rmsd':
            return self.page_indices['rmsd']

        # Go to the spectrum.replicated page.
        elif self.page_error_type.selection == 'repl':
            return self.page_indices['repl']


    def wizard_page_after_repl(self):
        """Set the page that comes after the spectrum.replicated page.

        @return:    The index of the next page.
        @rtype:     int
        """

        # Go to the spectrum.integration_points page.
        int_method = gui_to_str(self.page_intensity.int_method.GetValue())
        if int_method != 'height':
            return self.page_indices['pts']

        # Skip to the relax_fit.relax_time page.
        else:
            return self.page_indices['relax_time']


    def wizard_page_after_rmsd(self):
        """Set the page that comes after the spectrum.baseplane_rmsd page.

        @return:    The index of the next page.
        @rtype:     int
        """

        # Go to the spectrum.integration_points page.
        int_method = gui_to_str(self.page_intensity.int_method.GetValue())
        if int_method != 'height':
            return self.page_indices['pts']

        # Skip to the relax_fit.relax_time page.
        else:
            return self.page_indices['relax_time']


    def wizard_update_pts(self):
        """Update the spectrum.replicated page based on previous data."""

        # The spectrum.read_intensities page.
        page = self.wizard.get_page(self.page_indices['read'])

        # Set the spectrum ID.
        id = page.spectrum_id.GetValue()

        # Set the ID in the spectrum.replicated page.
        page = self.wizard.get_page(self.page_indices['pts'])
        page.spectrum_id1.SetValue(id)


    def wizard_update_repl(self):
        """Update the spectrum.replicated page based on previous data."""

        # The spectrum.read_intensities page.
        page = self.wizard.get_page(self.page_indices['read'])

        # Set the spectrum ID.
        id = page.spectrum_id.GetValue()

        # Set the ID in the spectrum.replicated page.
        page = self.wizard.get_page(self.page_indices['repl'])
        page.spectrum_id1.SetValue(id)


    def wizard_update_rmsd(self):
        """Update the spectrum.baseplane_rmsd page based on previous data."""

        # The spectrum.read_intensities page.
        page = self.wizard.get_page(self.page_indices['read'])

        # Set the spectrum ID.
        id = page.spectrum_id.GetValue()

        # Set the ID in the spectrum.baseplane_rmsd page.
        page = self.wizard.get_page(self.page_indices['rmsd'])
        page.spectrum_id.SetValue(id)


    def wizard_update_relax_time(self):
        """Update the relax_fit.relax_time page based on previous data."""

        # The spectrum.read_intensities page.
        page = self.wizard.get_page(self.page_indices['read'])

        # Set the spectrum ID.
        id = page.spectrum_id.GetValue()

        # Set the ID in the relax_fit.relax_time page.
        page = self.wizard.get_page(self.page_indices['relax_time'])
        page.spectrum_id.SetValue(id)



class Execute_rx(Execute):
    """The Rx analysis execution object."""

    def run_analysis(self):
        """Execute the calculation."""

        # Controller.
        if not status.debug and not status.test_mode:
            # Redirect relax output and errors to the controller.
            redir = Redirect_text(self.gui.controller)
            sys.stdout = redir
            sys.stderr = redir

        # Execute.
        Relax_fit(pipe_name=self.data.pipe_name, file_root=self.data.file_root, results_dir=self.data.save_dir, grid_inc=self.data.inc, mc_sim_num=self.data.mc_sim_num, view_plots=False)

        # Alias the relax data store data.
        data = ds.relax_gui.analyses[self.data_index]

        # Is there a results list (old results file support)?
        if not hasattr(data, 'results_list'):
            data.results_list = []

        # Add Rx grace plot to the results list.
        data.results_list.append(data.save_dir+sep+'grace'+sep+self.data.file_root+'.agr')
        data.results_list.append(data.save_dir+sep+'grace'+sep+'intensities_norm.agr')
