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
from gui.analyses.elements.bool_element import Boolean_ctrl
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
from gui.string_conv import gui_to_bool, gui_to_int, gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizards.peak_intensity import Peak_intensity_wizard
from lib.text.gui import dw, dwH, i0, kex, padw2, phi_ex, phi_exB, phi_exC, r1, r1rho, r1rho_prime, r2, r2a, r2b, r2eff
from pipe_control.mol_res_spin import exists_mol_res_spin_data, spin_loop
from pipe_control.pipes import has_bundle, has_pipe
from specific_analyses.relax_disp.disp_data import has_cpmg_exp_type, has_r1rho_exp_type
from specific_analyses.relax_disp.variables import MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_LIST_CPMG, MODEL_LIST_R1RHO, MODEL_LM63, MODEL_LM63_3SITE, MODEL_M61, MODEL_M61B, MODEL_MQ_CR72, MODEL_MQ_NS_CPMG_2SITE, MODEL_NOREX, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_R1RHO_2SITE, MODEL_R2EFF, MODEL_TP02, MODEL_TSMFK01
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

            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add(self.label)

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name
            ds.relax_gui.analyses[data_index].pipe_bundle = pipe_bundle

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].numeric_only = False
            ds.relax_gui.analyses[data_index].grid_inc = None
            ds.relax_gui.analyses[data_index].mc_sim_num = None
            ds.relax_gui.analyses[data_index].pre_run_dir = None
            ds.relax_gui.analyses[data_index].mc_sim_all_models = False
            ds.relax_gui.analyses[data_index].save_dir = self.gui.launch_dir

            # Set the default dispersion models based on the experiment type.
            ds.relax_gui.analyses[data_index].disp_models = [
                MODEL_R2EFF,
                MODEL_NOREX,
                MODEL_CR72,
                MODEL_NS_CPMG_2SITE_EXPANDED,
                MODEL_TP02,
                MODEL_NS_R1RHO_2SITE
            ]

        # Error checking.
        if ds.relax_gui.analyses[data_index].pipe_bundle == None:
            raise RelaxError("The pipe bundle must be supplied.")

        # Alias the data.
        self.data = ds.relax_gui.analyses[data_index]
        self.data_index = data_index

        # Register the method for updating the spin count for the completion of user functions.
        self.observer_register()

        # Execute the base class method to build the panel.
        super(Auto_relax_disp, self).__init__(parent, id=id, pos=pos, size=size, style=style, name=name)

        # Optimisation variables for speeding up the test suite.
        self.opt_func_tol = 1e-25
        self.opt_max_iterations = int(1e7)

        # Update the isotope and cluster information.
        self.update_clusters()


    def activate(self):
        """Activate or deactivate certain elements of the analysis in response to the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # Activate or deactivate the elements.
        wx.CallAfter(self.field_results_dir.Enable, enable)
        wx.CallAfter(self.field_pre_run_dir.Enable, enable)
        wx.CallAfter(self.spin_systems.Enable, enable)
        wx.CallAfter(self.field_cluster.Enable, enable)
        wx.CallAfter(self.button_isotope.Enable, enable)
        wx.CallAfter(self.button_r1.Enable, enable)
        wx.CallAfter(self.button_chemical_shift.Enable, enable)
        wx.CallAfter(self.button_interatom_define.Enable, enable)
        wx.CallAfter(self.peak_intensity.Enable, enable)
        wx.CallAfter(self.model_field.Enable, enable)
        wx.CallAfter(self.button_exec_relax.Enable, enable)


    def add_buttons(self, box):
        """Add all of the buttons.

        @param box:     The box element to pack the GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Sizer.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Isotope type button.
        self.button_isotope = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Spin isotope")
        self.button_isotope.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.nuclear_symbol", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_isotope.SetFont(font.normal)
        self.button_isotope.SetSize((-1, 25))
        self.button_isotope.SetToolTipString("Set the nuclear isotope types via the spin.isotope user function.")
        self.gui.Bind(wx.EVT_BUTTON, self.spin_isotope, self.button_isotope)
        sizer.Add(self.button_isotope, 1, wx.ALL|wx.EXPAND, 0)

        # R1 button.
        self.button_r1 = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " %s relaxation data"%r1)
        self.button_r1.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.fid", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_r1.SetFont(font.normal)
        self.button_r1.SetSize((-1, 25))
        self.button_r1.SetToolTipString("Load the %s relaxation data for the off-resonance %s-type experiments.  For all other experiment types this is unused.  One %s data set per magnetic field strength must be loaded."%(r1, r1rho, r1))
        self.gui.Bind(wx.EVT_BUTTON, self.load_r1_data, self.button_r1)
        sizer.Add(self.button_r1, 1, wx.ALL|wx.EXPAND, 0)

        # Chemical shift button.
        self.button_chemical_shift = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Chemical shift")
        self.button_chemical_shift.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.chemical_shift", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_chemical_shift.SetFont(font.normal)
        self.button_chemical_shift.SetSize((-1, 25))
        self.button_chemical_shift.SetToolTipString("Read chemical shifts from a peak list for the off-resonance %s-type experiments.  For all other experiment types this is unused."%r1rho)
        self.gui.Bind(wx.EVT_BUTTON, self.load_cs_data, self.button_chemical_shift)
        sizer.Add(self.button_chemical_shift, 1, wx.ALL|wx.EXPAND, 0)

        # Interatomic interaction button.
        self.button_interatom_define = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Interatomic interaction")
        self.button_interatom_define.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.dipole_pair", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_interatom_define.SetFont(font.normal)
        self.button_interatom_define.SetSize((-1, 25))
        self.button_interatom_define.SetToolTipString("Define the interatomic interations via the interatom.define user function for the MQ dispersion models.")
        self.gui.Bind(wx.EVT_BUTTON, self.interatom_define, self.button_interatom_define)
        sizer.Add(self.button_interatom_define, 1, wx.ALL|wx.EXPAND, 0)

        # value.set button.
        self.button_value_set = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Value setting")
        self.button_value_set.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.value", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_value_set.SetFont(font.normal)
        self.button_value_set.SetSize((-1, 25))
        tooltip = "Set certain parameters to experimentally determined values.\n\nThis is simply used to speed up optimisation by skipping this parameter in the initial grid search.  The result is that the number of dimensions in the grid search is decreased, resulting in roughly one order of magnitude decrease in time for each parameter in this part of the analysis.  Important to note is that the parameter will be optimised after the initial grid search."
        self.button_value_set.SetToolTipString(tooltip)
        self.gui.Bind(wx.EVT_BUTTON, self.value_set, self.button_value_set)
        sizer.Add(self.button_value_set, 1, wx.ALL|wx.EXPAND, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def assemble_data(self):
        """Assemble the data required for the Auto_noe class.

        @return:    A container with all the data required for the auto-analysis, the missing list, and a list of models that don't match the experiment types.
        @rtype:     class instance, list of str, list of str
        """

        # The data container.
        data = Container()
        missing = []
        model_mismatch = []

        # The pipe name and bundle.
        data.pipe_name = self.data.pipe_name
        data.pipe_bundle = self.data.pipe_bundle

        # Results directories.
        data.save_dir = self.data.save_dir
        data.pre_run_dir = gui_to_str(self.field_pre_run_dir.GetValue())

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

        # Invalid models.
        for model in data.models:
            # Invalid CPMG models.
            if model != MODEL_NOREX and model in MODEL_LIST_CPMG and not has_cpmg_exp_type():
                model_mismatch.append([model, 'CPMG'])

            # Invalid R1rho models.
            if model != MODEL_NOREX and model in MODEL_LIST_R1RHO and not has_r1rho_exp_type():
                model_mismatch.append([model, 'R1rho'])

        # The numeric only solution.
        data.numeric_only = self.numeric_only.GetValue()

        # Increment size.
        data.inc = gui_to_int(self.grid_inc.GetValue())

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        data.mc_sim_num = gui_to_int(self.mc_sim_num.GetValue())
        data.mc_sim_all_models = self.mc_sim_all_models.GetValue()

        # Optimisation precision.
        data.opt_func_tol = self.opt_func_tol
        data.opt_max_iterations = self.opt_max_iterations

        # Return the container, the list of missing data, and any models that don't match the experiment types.
        return data, missing, model_mismatch


    def build_right_box(self):
        """Construct the right hand box to pack into the main relax_disp box.

        @return:    The right hand box element containing all relaxation dispersion GUI elements (excluding the bitmap) to pack into the main box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_title(box, "Relaxation dispersion analysis")

        # Display the data pipe.
        Text_ctrl(box, self, text="The data pipe bundle:", default=self.data.pipe_bundle, tooltip="This is the data pipe bundle associated with this analysis.", editable=False, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the results directory GUI element.
        self.field_results_dir = Text_ctrl(box, self, text="Results directory:", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, tooltip="The directory in which all automatically created files will be saved.", tooltip_button="Select the results directory.", fn=self.results_directory, button=True, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the results directory GUI element.
        tooltip = "The optional directory containing the dispersion auto-analysis results from a previous run.  The optimised parameters from these previous results will be used as the starting point for optimisation rather than performing a grid search.  This is essential for when large spin clusters are specified, as a grid search becomes prohibitively expensive with clusters of three or more spins.  At some point a RelaxError will occur because the grid search is impossibly large.  For the cluster specific parameters, i.e. the populations of the states and the exchange parameters, an average value will be used as the starting point.  For all other parameters, the R20 values for each spin and magnetic field, as well as the parameters related to the chemical shift difference dw, the optimised values of the previous run will be directly copied."
        self.field_pre_run_dir = Text_ctrl(box, self, text="Previous run directory:", icon=paths.icon_16x16.open_folder, tooltip=tooltip, tooltip_button="Select the results directory of the previous run.", fn=self.pre_run_directory, button=True, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the spin GUI element.
        self.add_spin_systems(box, self)

        # Spin cluster setup.
        self.field_cluster = Text_ctrl(box, self, text="Spin cluster IDs:", button_text=" Cluster", icon=fetch_icon("relax.cluster", "16x16"), tooltip="The list of currently defined spin clusters.  A spin cluster will share the same the dispersion parameters during the optimisation of the dispersion model.  The special 'free spins' cluster ID refers to all non-clustered spins.", tooltip_button="Define clusters of spins using the relax_disp.cluster user function.", fn=self.relax_disp_cluster, button=True, editable=False, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the buttons.
        box.AddSpacer(20)
        self.add_buttons(box=box)

        # Add the peak list selection GUI element, with spacing.
        box.AddSpacer(20)
        self.peak_intensity = Spectra_list(gui=self.gui, parent=self, box=box, id=str(self.data_index), fn_add=self.peak_wizard_launch, relax_disp_flag=True)
        box.AddSpacer(10)

        # Add the dispersion models GUI element, with spacing.
        self.model_field = Disp_model_list(self, box)
        self.model_field.set_value(self.data.disp_models)

        # The numeric only solution.
        tooltip = "The class of models to use in the final model selection.\n\nThe default of False allows all dispersion models to be compared for statistical significance in the analysis (no exchange, the analytic models and the numeric models).  The value of True will activate a pure numeric solution - the analytic models will be optimised, as they are very useful for replacing the grid search for the numeric models, but the final model selection will not include them."
        self.numeric_only = Boolean_ctrl(box, self, text="Pure numeric solutions:", default=False, tooltip=tooltip, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # The grid search optimisation settings.
        self.grid_inc = Spin_ctrl(box, self, text="Grid search increments:", default=21, min=1, max=100, tooltip="This is the number of increments per dimension of the grid search performed prior to numerical optimisation.", width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # The MC simulation settings.
        self.mc_sim_num = Spin_ctrl(box, self, text="Monte Carlo simulation number:", default=500, min=1, max=100000, tooltip="This is the number of Monte Carlo simulations performed for error propagation and analysis.  For best results, at least 500 is recommended.", width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)
        self.mc_sim_all_models = Boolean_ctrl(box, self, text="Per model error analysis:", default=False, tooltip="A flag which if True will cause Monte Carlo simulations to be performed for each individual model.  Otherwise Monte Carlo simulations will be reserved for the final model.", width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

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
        data, missing, model_mismatch = self.assemble_data()

        # Missing data.
        if len(missing):
            Missing_data(missing)
            return

        # Model mismatch.
        if len(model_mismatch):
            # Generate the text.
            text = ''
            for model, exp in model_mismatch:
                text += "The '%s' %s model cannot be used as no %s experiment types have been set up.\n" % (model, exp, exp)

            # The error message.
            error_message(text, caption='Model mismatch')
            return

        # Display the relax controller, and go to the end of the log window.
        self.gui.show_controller(None)
        self.gui.controller.log_panel.on_goto_end(None)

        # Start the thread.
        self.thread = Execute_relax_disp(self.gui, data, self.data_index)
        self.thread.start()

        # Terminate the event.
        event.Skip()


    def interatom_define(self, event=None):
        """Define the interatomic interactions of the spins via the interatom.define user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['interatom.define'](wx_wizard_modal=True, spin_id1='@N', spin_id2='@H')


    def load_cs_data(self, event=None):
        """Read chemical shift data from a peak list via the chemical_shift.read user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['chemical_shift.read'](wx_wizard_modal=True)


    def load_r1_data(self, event=None):
        """Load R1 relaxation data via the relax_data.read user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['relax_data.read'](wx_wizard_modal=True, ri_type='R1')


    def observer_register(self, remove=False):
        """Register and unregister methods with the observer objects.

        @keyword remove:    If set to True, then the methods will be unregistered.
        @type remove:       False
        """

        # Register.
        if not remove:
            status.observers.gui_uf.register('spin count - %s' % self.data.pipe_bundle, self.update_spin_count, method_name='update_spin_count')
            status.observers.exec_lock.register(self.data.pipe_bundle, self.activate, method_name='activate')
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
        self.peak_wizard = Peak_intensity_wizard(relax_disp=True)


    def pre_run_directory(self, event):
        """The pre-run directory selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The dialog.
        dialog = RelaxDirDialog(parent=self, message='Select the directory of the previous run', defaultPath=self.field_pre_run_dir.GetValue())

        # Show the dialog and catch if no file has been selected.
        if status.show_gui and dialog.ShowModal() != wx.ID_OK:
            # Don't do anything.
            return

        # The path (don't do anything if not set).
        path = gui_to_str(dialog.get_path())
        if not path:
            return

        # Place the path in the text box.
        self.field_pre_run_dir.SetValue(str_to_gui(path))


    def relax_disp_cluster(self, event=None):
        """Set up spin clustering via the relax_disp.cluster user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['relax_disp.cluster'](wx_wizard_modal=True)


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

        # The numeric solution only flag.
        if upload:
            self.data.numeric_only = self.numeric_only.GetValue()
        elif hasattr(self.data, 'numeric_only'):
            self.numeric_only.SetValue(bool(self.data.numeric_only))

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

        # The All model MC sim flag.
        if upload:
            self.data.mc_sim_all_models = self.mc_sim_all_models.GetValue()
        elif hasattr(self.data, 'mc_sim_all_models'):
            self.mc_sim_all_models.SetValue(bool(self.data.mc_sim_all_models))

        # The results directory.
        if upload:
            self.data.save_dir = gui_to_str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str_to_gui(self.data.save_dir))

        # The previous run results directory.
        if upload:
            self.data.pre_run_dir = gui_to_str(self.field_pre_run_dir.GetValue())
        elif hasattr(self.data, 'pre_run_dir'):
            self.field_pre_run_dir.SetValue(str_to_gui(self.data.pre_run_dir))

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
            text = ""
            if "free spins" in cluster_keys:
                text += "free spins"
            for i in range(len(cluster_keys)):
                if cluster_keys[i] != "free spins":
                    text += ", %s" % cluster_keys[i]

            # Update the text.
            self.field_cluster.SetValue(text)


    def value_set(self, event=None):
        """Launch the value.set user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['value.set'](wx_wizard_modal=True)



class Execute_relax_disp(Execute):
    """The relaxation dispersion analysis execution object."""

    def run_analysis(self):
        """Execute the calculation."""

        # Optimisation precision.
        Relax_disp.opt_func_tol = self.data.opt_func_tol
        Relax_disp.opt_max_iterations = self.data.opt_max_iterations

        # Execute.
        Relax_disp(pipe_name=self.data.pipe_name, pipe_bundle=self.data.pipe_bundle, results_dir=self.data.save_dir, models=self.data.models, grid_inc=self.data.inc, mc_sim_num=self.data.mc_sim_num, pre_run_dir=self.data.pre_run_dir, mc_sim_all_models=self.data.mc_sim_all_models, numeric_only=self.data.numeric_only)

        # Alias the relax data store data.
        data = ds.relax_gui.analyses[self.data_index]



class Disp_model_list(Model_list):
    """The diffusion model list GUI element."""

    # Class variables.
    desc = "Relaxation dispersion models:"
    models = [
        MODEL_R2EFF,
        None,
        MODEL_NOREX,
        None,
        MODEL_LM63,
        MODEL_LM63_3SITE,
        MODEL_CR72,
        MODEL_CR72_FULL,
        MODEL_IT99,
        MODEL_TSMFK01,
        MODEL_NS_CPMG_2SITE_EXPANDED,
        MODEL_NS_CPMG_2SITE_3D,
        MODEL_NS_CPMG_2SITE_3D_FULL,
        MODEL_NS_CPMG_2SITE_STAR,
        MODEL_NS_CPMG_2SITE_STAR_FULL,
        None,
        MODEL_M61,
        MODEL_M61B,
        MODEL_DPL94,
        MODEL_TP02,
        MODEL_NS_R1RHO_2SITE,
        None,
        MODEL_MQ_CR72,
        MODEL_MQ_NS_CPMG_2SITE
    ]
    params = [
        "{%s/%s, %s}" % (r2eff, r1rho, i0),
        None,
        "{%s, ...}" % (r2),
        None,
        "{%s, ..., %s, %s}" % (r2, phi_ex, kex),
        "{%s, ..., %s, kB, %s, kC}" % (r2, phi_exB, phi_exC),
        "{%s, ..., pA, %s, %s}" % (r2, dw, kex),
        "{%s, %s, ..., pA, %s, %s}" % (r2a, r2b, dw, kex),
        "{%s, ..., %s, %s, %s}" % (r2, phi_ex, padw2, kex),
        "{%s, ..., %s, k_AB}" % (r2a, dw),
        "{%s, ..., pA, %s, %s}" % (r2, dw, kex),
        "{%s, ..., pA, %s, %s}" % (r2, dw, kex),
        "{%s, %s, ..., pA, %s, %s}" % (r2a, r2b, dw, kex),
        "{%s, ..., pA, %s, %s}" % (r2, dw, kex),
        "{%s, %s, ..., pA, %s, %s}" % (r2a, r2b, dw, kex),
        None,
        "{%s, ..., %s, %s}" % (r1rho_prime, phi_ex, kex),
        "{%s, ..., pA, %s, %s}" % (r1rho_prime, dw, kex),
        "{%s, ..., %s, %s}" % (r1rho_prime, phi_ex, kex),
        "{%s, ..., pA, %s, %s}" % (r1rho_prime, dw, kex),
        "{%s, ..., pA, %s, %s}" % (r1rho_prime, dw, kex),
        None,
        "{%s, ..., pA, %s, %s, %s}" % (r2, dw, dwH, kex),
        "{%s, ..., pA, %s, %s, %s}" % (r2, dw, dwH, kex)
    ]
    model_desc = [
        "The base model for determining the %s/%s values and errors for all other models." % (r2eff, r1rho),
        None,
        "The model for no chemical exchange relaxation.",
        None,
        "The original Luz and Meiboom (1963) 2-site fast exchange equation.",
        "The original Luz and Meiboom (1963) 3-site fast exchange equation.",
        "The Carver and Richards (1972) 2-site equation for all time scales (with %s = %s)." % (r2a, r2b),
        "The Carver and Richards (1972) 2-site equation for all time scales.",
        "The Ishima and Torchia (1999) 2-site model for all time scales with pA >> pB.",
        "The Tollinger et al. (2001) 2-site very-slow exchange model.",
        "The 2-site numerical solution expanded using Maple by Nikolai Skrynnikov.",
        "The 2-site numerical solution using 3D magnetisation vectors (with %s = %s)." % (r2a, r2b),
        "The 2-site numerical solution using 3D magnetisation vectors.",
        "The 2-site numerical solution using complex conjugate matrices (with %s = %s)." % (r2a, r2b),
        "The 2-site numerical solution using complex conjugate matrices.",
        None,
        "The Meiboom (1961) 2-site fast exchange equation.",
        "The Meiboom (1961) 2-site equation for all time scales with pA >> pB.",
        "The Davis, Perlman and London (1994) 2-site fast exchange equation.",
        "The Trott and Palmer (2002) 2-site equation for all time scales.",
        "The 2-site numerical solution using 3D magnetisation vectors.",
        None,
        "The CR72 2-site model extended to MQ CPMG data by Korzhnev et al., 2004.",
        "The 2-site numerical solution of Korzhnev et al. (2004) from multi-quantum CPMG data."
    ]
    tooltip = "The list of all relaxation dispersion models to be optimised as part of the protocol."
    tooltip_button = "Open the model list selector window."
