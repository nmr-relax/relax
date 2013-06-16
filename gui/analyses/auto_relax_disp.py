###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the automatic relaxation dispersion analysis."""

# Python module imports.
import wx

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from graphics import ANALYSIS_IMAGE_PATH, fetch_icon
from gui.analyses.base import Base_analysis
from gui.analyses.elements.spin_element import Spin_ctrl
from gui.analyses.elements.text_element import Text_ctrl
from gui.analyses.elements.model_list import Model_list
from gui.analyses.execute import Execute
from gui.base_classes import Container
from gui.components.spectrum import Spectra_list
from gui.filedialog import RelaxDirDialog
from gui.fonts import font
from gui.message import error_message, Missing_data
from gui import paths
from gui.string_conv import gui_to_int, gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizards.peak_intensity import Peak_intensity_wizard
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from pipe_control.pipes import has_bundle, has_pipe
from specific_analyses.relax_disp.variables import CPMG_EXP, MODEL_CR72, MODEL_DPL94, MODEL_IT99, MODEL_LIST_CPMG_FULL, MODEL_LIST_R1RHO_FULL, MODEL_LM63, MODEL_M61, MODEL_M61B, MODEL_NOREX, MODEL_R2EFF, VAR_TIME_EXP
from status import Status; status = Status()


class Auto_relax_disp(Base_analysis):
    """The relaxation dispersion auto-analysis GUI element."""

    # Hardcoded variables.
    analysis_type = None
    bitmap = ANALYSIS_IMAGE_PATH+"relax_disp_200x200.png"
    label = 'Relax-disp'

    def __init__(self, parent, id=-1, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=524288, name='scrolledpanel', gui=None, analysis_name=None, pipe_name=None, pipe_bundle=None, uf_exec=[], data_index=None):
        """Build the automatic R1 and R2 analysis GUI frame elements.

        @param parent:          The parent wx element.
        @type parent:           wx object
        @keyword id:            The unique ID number.
        @type id:               int
        @keyword pos:           The position.
        @type pos:              wx.Size object
        @keyword size:          The size.
        @type size:             wx.Size object
        @keyword style:         The style.
        @type style:            int
        @keyword name:          The name for the panel.
        @type name:             unicode
        @keyword gui:           The main GUI class.
        @type gui:              gui.relax_gui.Main instance
        @keyword analysis_name: The name of the analysis (the name in the tab part of the notebook).
        @type analysis_name:    str
        @keyword pipe_name:     The name of the data pipe associated with this analysis.
        @type pipe_name:        str
        @keyword pipe_bundle:   The name of the data pipe bundle associated with this analysis.
        @type pipe_bundle:      str
        @keyword uf_exec:       The list of user function on_execute methods returned from the new analysis wizard.
        @type uf_exec:          list of methods
        @keyword data_index:    The index of the analysis in the relax data store (set to None if no data currently exists).
        @type data_index:       None or int
        """

        # Store the GUI main class.
        self.gui = gui

        # Init.
        self.init_flag = True

        # New data container.
        if data_index == None:
            # First create the data pipe if not already in existence.
            if not has_pipe(pipe_name):
                self.gui.interpreter.apply('pipe.create', pipe_name=pipe_name, pipe_type='relax_disp', bundle=pipe_bundle)

            # Create the data pipe bundle if needed.
            if not has_bundle(pipe_bundle):
                self.gui.interpreter.apply('pipe.bundle', bundle=pipe_bundle, pipe=pipe_name)

            # Set up the experiment.
            if not hasattr(cdp, 'exp_type'):
                uf_exec[0](force_exec=True)

            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add(self.label)

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name
            ds.relax_gui.analyses[data_index].pipe_bundle = pipe_bundle

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].grid_inc = None
            ds.relax_gui.analyses[data_index].mc_sim_num = None
            ds.relax_gui.analyses[data_index].save_dir = self.gui.launch_dir

            # Set the dispersion models based on the experiment type.
            if cdp.exp_type in CPMG_EXP:
                ds.relax_gui.analyses[data_index].disp_models = MODEL_LIST_CPMG_FULL
            else:
                ds.relax_gui.analyses[data_index].disp_models = MODEL_LIST_R1RHO_FULL

        # Error checking.
        if ds.relax_gui.analyses[data_index].pipe_bundle == None:
            raise RelaxError("The pipe bundle must be supplied.")

        # Alias the data.
        self.data = ds.relax_gui.analyses[data_index]
        self.data_index = data_index

        # Register the method for updating the spin count for the completion of user functions.
        self.observer_register()

        # Set up some flags based on the experiment type.
        self.relax_times_flag = False
        if cdp.exp_type in VAR_TIME_EXP:
            self.relax_times_flag = True
        self.relax_disp_cpmg = False
        if cdp.exp_type in CPMG_EXP:
            self.relax_disp_cpmg = True

        # Execute the base class method to build the panel.
        super(Auto_relax_disp, self).__init__(parent, id=id, pos=pos, size=size, style=style, name=name)

        # Optimisation variables for speeding up the test suite.
        self.opt_func_tol = 1e-25
        self.opt_max_iterations = int(1e7)

        # Update the isotope and cluster information.
        self.update_isotopes()
        self.update_clusters()


    def activate(self):
        """Activate or deactivate certain elements of the analysis in response to the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # Activate or deactivate the elements.
        wx.CallAfter(self.field_results_dir.Enable, enable)
        wx.CallAfter(self.spin_systems.Enable, enable)
        wx.CallAfter(self.field_isotope.Enable, enable)
        wx.CallAfter(self.field_cluster.Enable, enable)
        wx.CallAfter(self.peak_intensity.Enable, enable)
        wx.CallAfter(self.model_field.Enable, enable)
        wx.CallAfter(self.button_exec_relax.Enable, enable)


    def assemble_data(self):
        """Assemble the data required for the Auto_noe class.

        @return:    A container with all the data required for the auto-analysis.
        @rtype:     class instance, list of str
        """

        # The data container.
        data = Container()
        missing = []

        # The pipe name and bundle.
        data.pipe_name = self.data.pipe_name
        data.pipe_bundle = self.data.pipe_bundle

        # Results directory.
        data.save_dir = self.data.save_dir

        # Check if sequence data is loaded
        if not exists_mol_res_spin_data():
            missing.append("Sequence data")

        # Spin variables.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # The message skeleton.
            msg = "Spin '%s' - %s (try the %s user function)." % (spin_id, "%s", "%s")

            # Test if the nuclear isotope type has been set.
            if not hasattr(spin, 'isotope') or spin.isotope == None:
                missing.append(msg % ("nuclear isotope data", "spin.isotope"))

        # Spectral data.
        if not hasattr(cdp, 'spectrum_ids') or len(cdp.spectrum_ids) < 2:
            missing.append("Spectral data")

        # The dispersion models.
        data.models = self.model_field.GetValue()

        # Increment size.
        data.inc = gui_to_int(self.grid_inc.GetValue())

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        data.mc_sim_num = gui_to_int(self.mc_sim_num.GetValue())

        # Optimisation precision.
        data.opt_func_tol = self.opt_func_tol
        data.opt_max_iterations = self.opt_max_iterations

        # Return the container and list of missing data.
        return data, missing


    def build_right_box(self):
        """Construct the right hand box to pack into the main relax_disp box.

        @return:    The right hand box element containing all relaxation dispersion GUI elements (excluding the bitmap) to pack into the main box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_title(box, "Relaxation dispersion analysis")

        # Display the experiment type.
        table = {
            "cpmg fixed": "CPMG-type experiment - fixed relaxation time period",
            "cpmg exponential": "CPMG-type experiment - Full exponential curve",
            "r1rho fixed": u"R\u2081\u1D68-type experiment - fixed relaxation time period",
            "r1rho exponential": u"R\u2081\u1D68-type experiment - full exponential curve"
        }
        Text_ctrl(box, self, text="Experiment type:", default=table[cdp.exp_type], tooltip="The relaxation dispersion experiment type.  The %s experiment type was selected in the new analysis wizard and can no longer be changed."%table[cdp.exp_type], editable=False, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Display the data pipe.
        Text_ctrl(box, self, text="The data pipe bundle:", default=self.data.pipe_bundle, tooltip="This is the data pipe bundle associated with this analysis.", editable=False, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the results directory GUI element.
        self.field_results_dir = Text_ctrl(box, self, text="Results directory:", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, tooltip="The directory in which all automatically created files will be saved.", tooltip_button="Select the results directory.", fn=self.results_directory, button=True, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the spin GUI element.
        self.add_spin_systems(box, self)

        # Spin cluster setup.
        self.field_cluster = Text_ctrl(box, self, text="Spin cluster IDs:", button_text=" Cluster", icon=fetch_icon("relax.cluster", "16x16"), tooltip="The list of currently defined spin clusters.  A spin cluster will share the same the dispersion parameters during the optimisation of the dispersion model.  The special 'free spins' cluster ID refers to all non-clustered spins.", tooltip_button="Define clusters of spins using the relax_disp.cluster user function.", fn=self.relax_disp_cluster, button=True, editable=False, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Spin isotope setup.
        self.field_isotope = Text_ctrl(box, self, text="Spin isotopes:", button_text=" Setup", icon=fetch_icon("relax.nuclear_symbol", "16x16"), tooltip="The list of nuclear isotopes of the spins to be used in the analysis.", tooltip_button="Execute the spin.isotope user function.", fn=self.spin_isotope, button=True, editable=False, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the peak list selection GUI element, with spacing.
        box.AddSpacer(20)
        self.peak_intensity = Spectra_list(gui=self.gui, parent=self, box=box, id=str(self.data_index), fn_add=self.peak_wizard_launch, relax_times=self.relax_times_flag, frq_flag=True, spin_lock_flag=(not self.relax_disp_cpmg), cpmg_frq_flag=self.relax_disp_cpmg)
        box.AddSpacer(10)

        # Add the dispersion models GUI element, with spacing.
        if cdp.exp_type in CPMG_EXP:
            self.model_field = Disp_model_list_cpmg(self, box)
        else:
            self.model_field = Disp_model_list_r1rho(self, box)
        self.model_field.set_value(self.data.disp_models)

        # The optimisation settings.
        self.grid_inc = Spin_ctrl(box, self, text="Grid search increments:", default=21, min=1, max=100, tooltip="This is the number of increments per dimension of the grid search performed prior to numerical optimisation.", width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)
        self.mc_sim_num = Spin_ctrl(box, self, text="Monte Carlo simulation number:", default=500, min=1, max=100000, tooltip="This is the number of Monte Carlo simulations performed for error propagation and analysis.  For best results, at least 500 is recommended.", width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Stretchable spacing (with a minimal space).
        box.AddSpacer(30)
        box.AddStretchSpacer()

        # Add the execution GUI element.
        self.button_exec_relax = self.add_execute_analysis(box, self.execute)

        # Return the box.
        return box


    def delete(self):
        """Unregister the spin count from the user functions."""

        # Unregister the observer methods.
        self.observer_register(remove=True)

        # Clean up the peak intensity object.
        self.peak_intensity.delete()


    def execute(self, event):
        """Set up, execute, and process the automatic Rx analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Flush the GUI interpreter internal queue to make sure all user functions are complete.
        self.gui.interpreter.flush()

        # relax execution lock.
        if status.exec_lock.locked():
            error_message("relax is currently executing.", "relax execution lock")
            event.Skip()
            return

        # User warning to close windows.
        self.gui.close_windows()

        # Synchronise the frame data to the relax data store.
        self.sync_ds(upload=True)

        # Assemble all the data needed for the auto-analysis.
        data, missing = self.assemble_data()

        # Missing data.
        if len(missing):
            Missing_data(missing)
            return

        # Display the relax controller, and go to the end of the log window.
        self.gui.show_controller(None)
        self.gui.controller.log_panel.on_goto_end(None)

        # Start the thread.
        self.thread = Execute_relax_disp(self.gui, data, self.data_index)
        self.thread.start()

        # Terminate the event.
        event.Skip()


    def observer_register(self, remove=False):
        """Register and unregister methods with the observer objects.

        @keyword remove:    If set to True, then the methods will be unregistered.
        @type remove:       False
        """

        # Register.
        if not remove:
            status.observers.gui_uf.register('spin count - %s' % self.data.pipe_bundle, self.update_spin_count, method_name='update_spin_count')
            status.observers.exec_lock.register(self.data.pipe_bundle, self.activate, method_name='activate')
            status.observers.gui_uf.register('isotopes - %s' % self.data.pipe_bundle, self.update_isotopes, method_name='update_isotopes')
            status.observers.gui_uf.register('clusters - %s' % self.data.pipe_bundle, self.update_clusters, method_name='update_clusters')

        # Unregister.
        else:
            # The methods.
            status.observers.gui_uf.unregister('spin count - %s' % self.data.pipe_bundle)
            status.observers.exec_lock.unregister(self.data.pipe_bundle)
            status.observers.gui_uf.unregister('isotopes - %s' % self.data.pipe_bundle)
            status.observers.gui_uf.unregister('clusters - %s' % self.data.pipe_bundle)

            # The embedded objects methods.
            self.peak_intensity.observer_register(remove=True)


    def peak_wizard_launch(self, event):
        """Launch the peak loading wizard.

        @param event:   The wx event.
        @type event:    wx event
        """

        # A new wizard instance.
        self.peak_wizard = Peak_intensity_wizard(relax_disp=True, relax_disp_cpmg=self.relax_disp_cpmg, relax_disp_times=self.relax_times_flag)


    def relax_disp_cluster(self, event=None):
        """Set up spin clustering via the relax_disp.cluster user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['relax_disp.cluster'](wx_wizard_modal=True)


    def relax_disp_exp_type(self, event):
        """Set the experiment type via the relax_disp.exp_type user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['relax_disp.exp_type'](wx_wizard_modal=True)

        # Place the experiment type in the text box.
        if hasattr(cdp, 'exp_type'):
            self.field_exp_type.SetValue(str_to_gui(cdp.exp_type))


    def results_directory(self, event):
        """The results directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The dialog.
        dialog = RelaxDirDialog(parent=self, message='Select the results directory', defaultPath=self.field_results_dir.GetValue())

        # Show the dialog and catch if no file has been selected.
        if status.show_gui and dialog.ShowModal() != wx.ID_OK:
            # Don't do anything.
            return

        # The path (don't do anything if not set).
        path = gui_to_str(dialog.get_path())
        if not path:
            return

        # Store the path.
        self.data.save_dir = path

        # Place the path in the text box.
        self.field_results_dir.SetValue(str_to_gui(path))


    def spin_isotope(self, event=None):
        """Set the nuclear isotope types of the spins via the spin.isotope user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['spin.isotope'](wx_wizard_modal=True, isotope='15N', spin_id='@N*')


    def sync_ds(self, upload=False):
        """Synchronise the analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

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

        # The models to use.
        if upload:
            self.data.disp_models = self.model_field.GetValue()
        else:
            self.model_field.set_value(self.data.disp_models)


    def update_clusters(self):
        """Update the cluster field."""

        # Assemble a list of all unique isotope types.
        cluster_keys = []
        if hasattr(cdp, 'clustering'):
            cluster_keys = sorted(cdp.clustering.keys())

        # Nothing yet.
        if not len(cluster_keys):
            self.field_cluster.SetValue("free spins")

        # List the clusters.
        else:
            # Build the text to show.
            if "free spins" in cluster_keys:
                text = "free spins"
            else:
                text = cluster_keys[0]
            for i in range(1, len(cluster_keys)):
                if cluster_keys[i] != "free spins":
                    text += ", %s" % cluster_keys[i]

            # Update the text.
            self.field_cluster.SetValue(text)


    def update_isotopes(self):
        """Update the isotope field."""

        # Assemble a list of all unique isotope types.
        isotopes = []
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            if hasattr(spin, 'isotope') and spin.isotope not in isotopes:
                isotopes.append(spin.isotope)

        # Nothing yet.
        if not len(isotopes):
            self.field_isotope.SetValue("Undefined")

        # List the isotopes.
        else:
            # Build the text to show.
            text = isotopes[0]
            for i in range(1, len(isotopes)):
                text += ", %s" % isotopes[i]

            # Update the text.
            self.field_isotope.SetValue(text)



class Execute_relax_disp(Execute):
    """The relaxation dispersion analysis execution object."""

    def run_analysis(self):
        """Execute the calculation."""

        # Optimisation precision.
        Relax_disp.opt_func_tol = self.data.opt_func_tol
        Relax_disp.opt_max_iterations = self.data.opt_max_iterations

        # Execute.
        Relax_disp(pipe_name=self.data.pipe_name, pipe_bundle=self.data.pipe_bundle, results_dir=self.data.save_dir, models=self.data.models, grid_inc=self.data.inc, mc_sim_num=self.data.mc_sim_num)

        # Alias the relax data store data.
        data = ds.relax_gui.analyses[self.data_index]



class Disp_model_list_cpmg(Model_list):
    """The diffusion model list GUI element."""

    # Class variables.
    desc = "Relaxation dispersion models:"
    models = [
        MODEL_R2EFF,
        MODEL_NOREX,
        MODEL_LM63,
        MODEL_CR72,
        MODEL_IT99
    ]
    params = [
        u"{R2eff, I\u2080}",
        u"{R\u2082, ...}",
        u"{R\u2082, ..., phi_ex, kex}",
        u"{R\u2082, ..., pA, d\u03C9, kex}",
        u"{R\u2082, ..., phi_ex, pA.d\u03C9^2, kex}"
    ]
    tooltip = "The list of all relaxation dispersion models to be optimised as part of the protocol."
    tooltip_button = "Open the model list selector window."



class Disp_model_list_r1rho(Model_list):
    """The diffusion model list GUI element."""

    # Class variables.
    desc = "Relaxation dispersion models:"
    models = [
        MODEL_R2EFF,
        MODEL_NOREX,
        MODEL_M61,
        MODEL_DPL94,
        MODEL_M61B
    ]
    params = [
        u"{R\u2081\u1D68, I\u2080}",
        u"{R\u2081\u1D68', ...}",
        u"{R\u2081\u1D68', ..., phi_ex, kex}",
        u"{R\u2081\u1D68', ..., phi_ex, kex}",
        u"{R\u2081\u1D68', ..., pA, d\u03C9, kex}",
    ]
    tooltip = "The list of all relaxation dispersion models to be optimised as part of the protocol."
    tooltip_button = "Open the model list selector window."
