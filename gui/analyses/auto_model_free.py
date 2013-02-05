###############################################################################
#                                                                             #
# Copyright (C) 2009 Michael Bieri                                            #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
"""Module for the automatic model-free protocol frame."""

# Python module imports.
from math import ceil
from os import sep
import sys
import wx
import wx.lib.buttons
import wx.lib.mixins.listctrl

# relax module imports.
from auto_analyses import dauvergne_protocol
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.interatomic import interatomic_loop
from generic_fns.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from generic_fns.pipes import has_bundle, has_pipe
from graphics import fetch_icon
from physical_constants import NH_BOND_LENGTH
from relax_errors import RelaxError
from relax_string import LIST, PARAGRAPH, SECTION, SUBSECTION, TITLE
from specific_fns.setup import get_specific_fn
from status import Status; status = Status()

# relax GUI module imports.
from gui.about import About_base
from gui.analyses.base import Base_analysis
from gui.analyses.elements import Spin_ctrl, Text_ctrl
from gui.analyses.execute import Execute
from gui.base_classes import Container
from gui.components.relax_data import Relax_data_list
from gui.filedialog import RelaxDirDialog
from gui.fonts import font
from gui.message import error_message, Question, Missing_data
from gui.misc import add_border, bitmap_setup, protected_exec
from gui import paths
from gui.string_conv import gui_to_int, gui_to_str, list_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizard import Wiz_window


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

        # A global Y offset for packing the elements together (initialise to the border position).
        self.offset(self.border)

        # Loop over the lines.
        for i in range(len(dauvergne_protocol.doc)):
            # The level and text.
            level, text = dauvergne_protocol.doc[i]

            # The title.
            if level == TITLE:
                self.draw_title(text, alt_font=font.roman_font_18)

            # The section.
            elif level == SECTION:
                self.draw_title(text, alt_font=font.roman_font_14)

            # The section.
            elif level == SUBSECTION:
                self.draw_title(text, alt_font=font.roman_font_12)

            # Paragraphs.
            elif level == PARAGRAPH:
                self.draw_wrapped_text(text)

            # Lists.
            elif level == LIST:
                # Start of list.
                if i and dauvergne_protocol.doc[i-1][0] != LIST:
                    self.offset(10)

                # The text.
                self.draw_wrapped_text("    - %s" % text)

                # End of list.
                if i < len(dauvergne_protocol.doc) and dauvergne_protocol.doc[i+1][0] == PARAGRAPH:
                    self.offset(10)

        # Add space to the bottom.
        self.offset(self.border)

        # Round the offset up to the nearest factor of the scroll inc (needed for all scrolling).
        scroll_x, scroll_y = self.window.GetScrollPixelsPerUnit()
        y = self.offset()
        self.offset(-y)
        y = int(ceil(y/float(scroll_y)) * scroll_y)
        self.offset(y)

        # Resize the window.
        dim_x = self.dim_x
        virt_y = self.offset()
        self.SetSize((dim_x, self.dim_y))
        self.window.SetVirtualSize((dim_x, virt_y))
        self.window.EnableScrolling(x_scrolling=False, y_scrolling=True)



class Auto_model_free(Base_analysis):
    """The model-free auto-analysis GUI element."""

    def __init__(self, parent, id=-1, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=524288, name='scrolledpanel', gui=None, analysis_name=None, pipe_name=None, pipe_bundle=None, data_index=None):
        """Build the automatic model-free protocol GUI element.

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
        @keyword pipe_name:     The name of the original data pipe for this analysis.
        @type pipe_name:        str
        @keyword pipe_bundle:   The name of the data pipe bundle associated with this analysis.
        @type pipe_bundle:      str
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
                self.gui.interpreter.apply('pipe.create', pipe_name=pipe_name, pipe_type='mf', bundle=pipe_bundle)

            # Create the data pipe bundle if needed.
            if not has_bundle(pipe_bundle):
                self.gui.interpreter.apply('pipe.bundle', bundle=pipe_bundle, pipe=pipe_name)

            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add('model-free')

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name
            ds.relax_gui.analyses[data_index].pipe_bundle = pipe_bundle

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].grid_inc = None
            ds.relax_gui.analyses[data_index].diff_tensor_grid_inc = {'sphere': 11, 'prolate': 11, 'oblate': 11, 'ellipsoid': 6}
            ds.relax_gui.analyses[data_index].mc_sim_num = None
            ds.relax_gui.analyses[data_index].save_dir = self.gui.launch_dir
            ds.relax_gui.analyses[data_index].local_tm_models = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
            ds.relax_gui.analyses[data_index].mf_models = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
            ds.relax_gui.analyses[data_index].max_iter = 30

        # Error checking.
        if ds.relax_gui.analyses[data_index].pipe_bundle == None:
            raise RelaxError("The pipe bundle must be supplied.")

        # Alias the data.
        self.data = ds.relax_gui.analyses[data_index]
        self.data_index = data_index

        # Backward compatibility.
        if not hasattr(self.data, 'local_tm_models'):
            self.data.local_tm_models = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
        if not hasattr(self.data, 'mf_models'):
            self.data.mf_models = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']

        # Initialise the mode selection window.
        self.mode_win = Protocol_mode_sel_window()

        # Register the method for updating the spin count for the completion of user functions.
        self.observer_register()

        # Execute the base class method to build the panel.
        super(Auto_model_free, self).__init__(parent, id=id, pos=pos, size=size, style=style, name=name)


    def _about(self, event=None):
        """The about window.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Initialise the dialog.
        self.about_dialog = About_window(self)

        # Show the dialog.
        if status.show_gui:
            self.about_dialog.Show()


    def activate(self):
        """Activate or deactivate certain elements of the analysis in response to the execution lock."""

        # Flag for enabling or disabling the elements.
        enable = False
        if not status.exec_lock.locked():
            enable = True

        # Activate or deactivate the elements.
        wx.CallAfter(self.field_results_dir.Enable, enable)
        wx.CallAfter(self.spin_systems.Enable, enable)
        wx.CallAfter(self.relax_data.Enable, enable)
        wx.CallAfter(self.button_dipole_pair.Enable, enable)
        wx.CallAfter(self.button_csa.Enable, enable)
        wx.CallAfter(self.button_isotope_heteronuc.Enable, enable)
        wx.CallAfter(self.button_isotope_proton.Enable, enable)
        wx.CallAfter(self.local_tm_model_field.Enable, enable)
        wx.CallAfter(self.mf_model_field.Enable, enable)
        wx.CallAfter(self.grid_inc.Enable, enable)
        wx.CallAfter(self.mc_sim_num.Enable, enable)
        wx.CallAfter(self.max_iter.Enable, enable)
        wx.CallAfter(self.mode.Enable, enable)
        wx.CallAfter(self.button_exec_relax.Enable, enable)


    def add_values(self, box):
        """Create and add the value.set buttons for the model-free analysis.

        @param box:     The box element to pack the GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Sizer.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Dipole-dipole relaxation setup button.
        self.button_dipole_pair = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " Dipolar relaxation")
        self.button_dipole_pair.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.dipole_pair", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_dipole_pair.SetFont(font.normal)
        self.button_dipole_pair.SetSize((-1, 25))
        self.button_dipole_pair.SetToolTipString("Define the magnetic dipole-dipole relaxation mechanism.")
        self.gui.Bind(wx.EVT_BUTTON, self.setup_dipole_pair, self.button_dipole_pair)
        sizer.Add(self.button_dipole_pair, 1, wx.ALL|wx.EXPAND, 0)

        # CSA button.
        self.button_csa = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " CSA relaxation")
        self.button_csa.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.align_tensor", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_csa.SetFont(font.normal)
        self.button_csa.SetSize((-1, 25))
        self.button_csa.SetToolTipString("Define the Chemical Shift Anisotropy (CSA) relaxation mechanism via the value.set user function.")
        self.gui.Bind(wx.EVT_BUTTON, self.value_set_csa, self.button_csa)
        sizer.Add(self.button_csa, 1, wx.ALL|wx.EXPAND, 0)

        # Isotope type button (heteronucleus).
        self.button_isotope_heteronuc = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " X isotope")
        self.button_isotope_heteronuc.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.nuclear_symbol", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_isotope_heteronuc.SetFont(font.normal)
        self.button_isotope_heteronuc.SetSize((-1, 25))
        self.button_isotope_heteronuc.SetToolTipString("Set the nuclear isotope types of the heteronuclear spins via the spin.isotope user function.")
        self.gui.Bind(wx.EVT_BUTTON, self.spin_isotope_heteronuc, self.button_isotope_heteronuc)
        sizer.Add(self.button_isotope_heteronuc, 1, wx.ALL|wx.EXPAND, 0)

        # Isotope type button (proton).
        self.button_isotope_proton = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, " H isotope")
        self.button_isotope_proton.SetBitmapLabel(wx.Bitmap(fetch_icon("relax.nuclear_symbol", "22x22"), wx.BITMAP_TYPE_ANY))
        self.button_isotope_proton.SetFont(font.normal)
        self.button_isotope_proton.SetSize((-1, 25))
        self.button_isotope_proton.SetToolTipString("Set the nuclear isotope types of the proton spins via the spin.isotope user function.")
        self.gui.Bind(wx.EVT_BUTTON, self.spin_isotope_proton, self.button_isotope_proton)
        sizer.Add(self.button_isotope_proton, 1, wx.ALL|wx.EXPAND, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def assemble_data(self):
        """Assemble the data required for the auto-analysis.

        See the docstring for auto_analyses.dauvernge_protocol for details.  All data is taken from the relax data store, so data upload from the GUI to there must have been previously performed.

        @return:    A container with all the data required for the auto-analysis.
        @rtype:     class instance, list of str
        """

        # The data container.
        data = Container()
        missing = []

        # The pipe name and bundle.
        data.pipe_name = self.data.pipe_name
        data.pipe_bundle = self.data.pipe_bundle

        # The model-free models (do not change these unless absolutely necessary).
        data.local_tm_models = self.local_tm_model_field.GetValue()
        data.mf_models = self.mf_model_field.GetValue()

        # Automatic looping over all rounds until convergence (must be a boolean value of True or False).
        data.conv_loop = True

        # Increment size.
        data.inc = gui_to_int(self.grid_inc.GetValue())
        if hasattr(self.data, 'diff_tensor_grid_inc'):
            data.diff_tensor_grid_inc = self.data.diff_tensor_grid_inc
        else:
            data.diff_tensor_grid_inc = {'sphere': 11, 'prolate': 11, 'oblate': 11, 'ellipsoid': 6}

        # The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        data.mc_sim_num = gui_to_int(self.mc_sim_num.GetValue())

        # Number of maximum iterations.
        data.max_iter = self.data.max_iter

        # Results directory.
        data.save_dir = self.data.save_dir

        # Check if sequence data is loaded
        if not exists_mol_res_spin_data():
            missing.append("Sequence data")

        # Relaxation data.
        if not hasattr(cdp, 'ri_ids') or len(cdp.ri_ids) == 0:
            missing.append("Relaxation data")

        # Insufficient data.
        if hasattr(cdp, 'ri_ids') and len(cdp.ri_ids) <= 3:
            missing.append("Insufficient relaxation data, 4 or more data sets are essential for the execution of the dauvergne_protocol auto-analysis.")

        # Interatomic data containers.
        if not hasattr(cdp, 'interatomic') or len(cdp.interatomic) == 0:
            missing.append("Interatomic data (for the dipole-dipole interaction)")

        # Get the mode.
        mode = gui_to_str(self.mode.GetValue())

        # Solve for all global models.
        if mode == 'Fully automated':
            # The global model list.
            data.global_models = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid', 'final']

        # Any global model selected.
        else:
            data.global_models = [mode]

        # Check for vectors.
        vector_check = False
        if 'prolate' in data.global_models or 'oblate' in data.global_models or 'ellipsoid' in data.global_models:
            vector_check = True

        # Spin variables.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # The message skeleton.
            msg = "Spin '%s' - %s (try the %s user function)." % (spin_id, "%s", "%s")

            # Test if the nuclear isotope type has been set.
            if not hasattr(spin, 'isotope') or spin.isotope == None:
                missing.append(msg % ("nuclear isotope data", "spin.isotope"))

            # Test if the CSA value has been set for the heteronuclei.
            if spin.isotope in ['15N', '13C'] and (not hasattr(spin, 'csa') or spin.csa == None):
                missing.append(msg % ("CSA data", "value.set"))

        # Interatomic data container variables.
        for interatom in interatomic_loop():
            # Get the spin containers.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # Skip deselected spins.
            if not spin1.select:
                continue
            if not spin2.select:
                continue

            # The message skeleton.
            msg = "Spin pair '%s' and '%s' - %s (try the %s user function)." % (interatom.spin_id1, interatom.spin_id2, "%s", "%s")

            # Test if the interatomic distance has been set.
            if not hasattr(interatom, 'r') or interatom.r == None:
                missing.append(msg % ("bond length data", "value.set"))

            # Test if the unit vectors have been loaded.
            if vector_check and (not hasattr(interatom, 'vector') or interatom.vector == None):
                missing.append(msg % ("unit vectors", "dipole_pair.unit_vectors"))

        # Return the container and list of missing data.
        return data, missing


    def build_left_box(self):
        """Construct the left hand box to pack into the main model-free box.

        @return:    The left hand box element containing the bitmap and about button to pack into the main model-free box.
        @rtype:     wx.BoxSizer instance
        """

        # Build the left hand box.
        left_box = wx.BoxSizer(wx.VERTICAL)

        # The images.
        bitmaps = [paths.ANALYSIS_IMAGE_PATH+"model_free"+sep+"model_free_200x200.png",
                   paths.IMAGE_PATH+'modelfree.png']

        # Add the model-free bitmap picture.
        for i in range(len(bitmaps)):
            # The bitmap.
            bitmap = wx.StaticBitmap(self, -1, bitmap_setup(bitmaps[i]))

            # Add it.
            left_box.Add(bitmap, 0, wx.ALL, 0)

        # A spacer.
        left_box.AddStretchSpacer()

        # A button sizer, with some initial spacing.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # An about button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "About")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.about, wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Information about this automatic analysis")

        # Bind the click.
        self.Bind(wx.EVT_BUTTON, self._about, button)

        # A cursor for the button.
        cursor = wx.StockCursor(wx.CURSOR_QUESTION_ARROW)
        button.SetCursor(cursor)

        # Pack the button.
        button_sizer.Add(button, 0, 0, 0)
        left_box.Add(button_sizer, 0, wx.ALL, 0)

        # Return the packed box.
        return left_box


    def build_right_box(self):
        """Construct the right hand box to pack into the main model-free box.

        @return:    The right hand box element containing all model-free GUI elements (excluding the bitmap) to pack into the main model-free box.
        @rtype:     wx.BoxSizer instance
        """

        # Use a vertical packing of elements.
        box = wx.BoxSizer(wx.VERTICAL)

        # Add the frame title.
        self.add_title(box, "Setup for model-free analysis")

        # Display the data pipe.
        Text_ctrl(box, self, text="The data pipe bundle:", default=self.data.pipe_bundle, tooltip="This is the data pipe bundle associated with this analysis.", editable=False, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the results directory GUI element.
        self.field_results_dir = Text_ctrl(box, self, text="Results directory", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, fn=self.results_directory, button=True, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add the spin GUI element.
        self.add_spin_systems(box, self)

        # Add the relaxation data list GUI element, with spacing.
        box.AddSpacer(10)
        self.relax_data = Relax_data_list(gui=self.gui, parent=self, box=box, id=str(self.data_index))
        box.AddSpacer(10)

        # Add the value.set buttons.
        self.add_values(box)
        box.AddSpacer(10)

        # Add the local tau_m models GUI element, with spacing.
        self.local_tm_model_field = Local_tm_list(self, box)
        self.local_tm_model_field.set_value(self.data.local_tm_models)

        # Add the model-free models GUI element, with spacing.
        self.mf_model_field = Mf_list(self, box)
        self.mf_model_field.set_value(self.data.mf_models)

        # The optimisation settings.
        self.grid_inc = Spin_ctrl(box, self, text="Grid search increments:", default=11, min=1, max=100, tooltip="This is the number of increments per dimension of the grid search performed prior to numerical optimisation.", width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)
        self.mc_sim_num = Spin_ctrl(box, self, text="Monte Carlo simulation number:", default=500, min=1, max=100000, tooltip="This is the number of Monte Carlo simulations performed for error propagation and analysis.", width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Add maximum iteration selector.
        self.max_iter = Spin_ctrl(box, self, text="Maximum interations", default=self.data.max_iter, min=25, max=100, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # The calculation mode.
        self.mode = Text_ctrl(box, self, text="Protocol mode:", default='Fully automated', tooltip="Select if the dauvergne_protocol analysis will be fully automated or whether the individual global models will be optimised one by one.", icon=paths.icon_16x16.system_run, fn=self.mode_dialog, editable=False, button=True, width_text=self.width_text, width_button=self.width_button, spacer=self.spacer_horizontal)

        # Stretchable spacing (with a minimal space).
        box.AddSpacer(30)
        box.AddStretchSpacer()

        # Add the execution GUI element.
        self.button_exec_relax = self.add_execute_relax(box, self.execute)

        # Return the box.
        return box


    def delete(self):
        """Unregister the spin count from the user functions."""

        # Unregister the observer methods.
        self.observer_register(remove=True)

        # Clean up the relaxation data list object.
        self.relax_data.delete()


    def execute(self, event=None):
        """Set up, execute, and process the automatic model-free protocol.

        @keyword event: The wx event.
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
        self.thread = Execute_mf(self.gui, data, self.data_index)
        self.thread.start()

        # Terminate the event.
        event.Skip()


    def mode_dialog(self, event=None):
        """The calculation mode selection.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Show the model selector window.
        if status.show_gui:
            self.mode_win.ShowModal()

        # Set the model.
        self.mode.SetValue(str_to_gui(self.mode_win.select))


    def observer_register(self, remove=False):
        """Register and unregister methods with the observer objects.

        @keyword remove:    If set to True, then the methods will be unregistered.
        @type remove:       False
        """

        # Register.
        if not remove:
            status.observers.gui_uf.register(self.data.pipe_bundle, self.update_spin_count, method_name='update_spin_count')
            status.observers.exec_lock.register(self.data.pipe_bundle, self.activate, method_name='activate')

        # Unregister.
        else:
            # The model-free methods.
            status.observers.gui_uf.unregister(self.data.pipe_bundle)
            status.observers.exec_lock.unregister(self.data.pipe_bundle)

            # The embedded objects methods.
            self.relax_data.observer_register(remove=True)


    def results_directory(self, event=None):
        """The results directory selection.

        @keyword event: The wx event.
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


    def setup_dipole_pair(self, event=None):
        """Create the wizard for the dipole-dipole interaction.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Change the cursor to busy.
        wx.BeginBusyCursor()

        # Create the wizard.
        self.dipole_wizard = Wiz_window(parent=self.gui, size_x=1000, size_y=750, title="Dipole-dipole interaction setup")

        # Structural data.
        if not hasattr(cdp, 'structure'):
            # Create the PDB reading page.
            page = uf_store['structure.read_pdb'].create_page(self.dipole_wizard)
            self.dipole_wizard.add_page(page, skip_button=True)

            # Create the position reading page.
            page = uf_store['structure.get_pos'].create_page(self.dipole_wizard)
            self.dipole_wizard.add_page(page, skip_button=True)

        # Create the dipole_pair.define page.
        page = uf_store['dipole_pair.define'].create_page(self.dipole_wizard)
        page.SetValue('spin_id1', '@N')
        page.SetValue('spin_id2', '@H')
        self.dipole_wizard.add_page(page)

        # Create the dipole_pair.set_dist page.
        page = uf_store['dipole_pair.set_dist'].create_page(self.dipole_wizard)
        page.SetValue('spin_id1', '@N*')
        page.SetValue('spin_id2', '@H*')
        page.SetValue('ave_dist', NH_BOND_LENGTH)
        self.dipole_wizard.add_page(page)

        # Create the dipole_pair.unit_vectors page.
        page = uf_store['dipole_pair.unit_vectors'].create_page(self.dipole_wizard)
        self.dipole_wizard.add_page(page)

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()

        # Execute the wizard.
        self.dipole_wizard.run()


    def spin_isotope_heteronuc(self, event=None):
        """Set the nuclear isotope types of the heteronuclear spins via the spin.isotope user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['spin.isotope'](isotope='15N', spin_id='@N*')


    def spin_isotope_proton(self, event=None):
        """Set the nuclear isotope types of the proton spins via the spin.isotope user function.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Call the user function.
        uf_store['spin.isotope'](isotope='1H', spin_id='@H*')


    def sync_ds(self, upload=False):
        """Synchronise the analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The local tau_m models to use.
        if upload:
            self.data.local_tm_models = self.local_tm_model_field.GetValue()
        else:
            self.local_tm_model_field.set_value(self.data.local_tm_models)

        # The model-free models to use.
        if upload:
            self.data.mf_models = self.mf_model_field.GetValue()
        else:
            self.mf_model_field.set_value(self.data.mf_models)

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
            self.data.save_dir = str(self.field_results_dir.GetValue())
        else:
            self.field_results_dir.SetValue(str_to_gui(self.data.save_dir))

        # Maximum iterations.
        if upload:
            self.data.max_iter = gui_to_int(self.max_iter.GetValue())
        else:
            self.max_iter.SetValue(int(self.data.max_iter))


    def value_set_csa(self, event=None):
        """Set the CSA via the value.set uf.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Get the default value.
        val = get_specific_fn('default_value')('csa')

        # Call the user function.
        uf_store['value.set'](val=val, param='csa', spin_id='@N*')



class Execute_mf(Execute):
    """The model-free analysis execution object."""

    def run_analysis(self):
        """Execute the calculation."""

        # Start the protocol.
        dauvergne_protocol.dAuvergne_protocol(pipe_name=self.data.pipe_name, pipe_bundle=self.data.pipe_bundle, results_dir=self.data.save_dir, diff_model=self.data.global_models, mf_models=self.data.mf_models, local_tm_models=self.data.local_tm_models, grid_inc=self.data.inc, diff_tensor_grid_inc=self.data.diff_tensor_grid_inc, mc_sim_num=self.data.mc_sim_num, max_iter=self.data.max_iter, conv_loop=self.data.conv_loop)



class Local_tm_list:
    """The model-free model list GUI element."""

    # Some class variables.
    desc = u'Local \u03C4m models:'
    models = [
        "tm0",
        "tm1",
        "tm2",
        "tm3",
        "tm4",
        "tm5",
        "tm6",
        "tm7",
        "tm8",
        "tm9"
    ]
    params = [
        "{local_tm}",
        "{local_tm, S2}",
        "{local_tm, S2, te}",
        "{local_tm, S2, Rex}",
        "{local_tm, S2, te, Rex}",
        "{local_tm, S2, S2f, ts}",
        "{local_tm, S2, tf, S2f, ts}",
        "{local_tm, S2, S2f, ts, Rex}",
        "{local_tm, S2, tf, S2f, ts, Rex}",
        "{local_tm, Rex}"
    ]

    def __init__(self, parent, box):
        """Build the combo box list widget for a list of list selections.

        @param parent:      The parent GUI element.
        @type parent:       wx object instance
        @param box:         The sizer to put the combo box widget into.
        @type box:          wx.Sizer instance
        """

        # Store some args.
        self.parent = parent

        # Initialise all models as being selected.
        self.select = []
        for i in range(len(self.models)):
            self.select.append(True)

        # Initialise the model selection window.
        self.model_win = Model_sel_window(self.models, self.params)

        # Horizontal packing for this element.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add a label.
        label = self.parent.add_static_text(sizer, self.parent, text=self.desc, width=self.parent.width_text)

        # Spacer.
        sizer.AddSpacer((self.parent.spacer_horizontal, -1))

        # The text input field.
        self.field = self.parent.add_text_control(sizer, self.parent, text=list_to_gui(self.GetValue()), editable=False)

        # Spacer.
        sizer.AddSpacer((self.parent.spacer_horizontal, -1))

        # Add the button.
        self.button = self.parent.add_button_open(sizer, self.parent, icon=paths.icon_16x16.flag_blue, text="Modify", fn=self.modify, width=self.parent.width_button, height=label.GetSize()[1]+8)

        # Add the contents to the main box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def Enable(self, enable=True):
        """Enable or disable the element.

        @keyword enable:    The flag specifying if the element should be enabled or disabled.
        @type enable:       bool
        """

        # Call the control and button's method.
        self.field.Enable(enable)
        self.button.Enable(enable)


    def GetValue(self):
        """Return the list of model-free models.

        @return:    The list of model-free models.
        @rtype:     list of str
        """

        # Initialise.
        model_list = []

        # Add the models if they are selected.
        for i in range(len(self.models)):
            if self.select[i]:
                model_list.append(self.models[i])

        # Return the list.
        return model_list


    def set_value(self, value):
        """Store the list of model-free models.

        @param value:   The list of model-free models.
        @type value:    list of str
        """

        # First set all models as being deselected.
        for i in range(len(self.models)):
            self.select[i] = False

        # Select all models in the list.
        for model in value:
            # The model index.
            index = self.models.index(model)

            # Set the selected flag.
            self.select[index] = True

        # Update the button.
        self.update_button()

        # Update the GUI element.
        self.field.SetValue(list_to_gui(self.GetValue()))


    def modify(self, event=None):
        """Modify the model-free model selection.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # First state that this should not be done.
        msg = "The model-free models used in dauvergne_protocol auto-analysis should almost never be changed!  The consequences will be unpredictable.  Please proceed only if you are sure of what you are doing.  Would you like to modify the model-free model list?"
        if status.show_gui and not Question(msg, title="Warning - do not change!", size=(420, 210), default=False).ShowModal() == wx.ID_YES:
            return

        # Set the model selector window selections.
        self.model_win.set_selection(self.select)

        # Show the model selector window.
        if status.show_gui:
            self.model_win.ShowModal()
            self.model_win.Close()

        # Set the values.
        self.select = self.model_win.get_selection()

        # Update the button.
        self.update_button()

        # Update the GUI element.
        self.field.SetValue(list_to_gui(self.GetValue()))


    def update_button(self):
        """Update the button bitmap as needed."""

        # Change the flag to red to indicate to the user that changing the models is a bad thing!
        if False in self.select:
            self.button.SetBitmapLabel(wx.Bitmap(paths.icon_16x16.flag_red, wx.BITMAP_TYPE_ANY))

        # Otherwise set it to blue (in case all models are selected again).
        else:
            self.button.SetBitmapLabel(wx.Bitmap(paths.icon_16x16.flag_blue, wx.BITMAP_TYPE_ANY))



class Mf_list(Local_tm_list):
    """The model-free model list GUI element."""

    # Some class variables.
    desc = "Model-free models:"
    models = [
        "m0",
        "m1",
        "m2",
        "m3",
        "m4",
        "m5",
        "m6",
        "m7",
        "m8",
        "m9"
    ]
    params = [
        "{}",
        "{S2}",
        "{S2, te}",
        "{S2, Rex}",
        "{S2, te, Rex}",
        "{S2, S2f, ts}",
        "{S2, tf, S2f, ts}",
        "{S2, S2f, ts, Rex}",
        "{S2, tf, S2f, ts, Rex}",
        "{Rex}"
    ]



class Model_sel_window(wx.Dialog):
    """The model-free model selector window object."""

    def __init__(self, models, params):
        """Set up the model-free model selector window.

        @param models:  The list of model-free models.
        @type models:   list of str
        @param params:  The list of parameters corresponding to the models.
        @type params:   list of str
        """

        # Set up the dialog.
        wx.Dialog.__init__(self, None, id=-1, title="Model-free model selector")

        # Initialise some values
        size_x = 500
        size_y = 300
        border = 10
        width = size_x - 2*border

        # Set the frame properties.
        self.SetSize((size_x, size_y))
        self.Centre()
        self.SetFont(font.normal)

        # The main box sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=border, packing=wx.VERTICAL)

        # Add a list control.
        self.model_list = ModelSelListCtrl(self)

        # The headers.
        self.model_list.InsertColumn(0, "Model-free model")
        self.model_list.InsertColumn(1, "Parameters")

        # The widths.
        self.model_list.SetColumnWidth(0, int(0.4*width))
        self.model_list.SetColumnWidth(1, int(0.5*width))

        # Add the models and parameters.
        for i in range(len(models)):
            # Set the text.
            self.model_list.Append((str_to_gui(models[i]), str_to_gui(params[i])))

            # Set all selections to True.
            self.model_list.CheckItem(i)

        # Add the table to the sizer.
        sizer.Add(self.model_list, 1, wx.ALL|wx.EXPAND, 0)


    def get_selection(self):
        """Return the selection as a list of booleans.

        @return:    The list of models selected.
        @rtype:     list of bool
        """

        # Init.
        select = []

        # Loop over the entries.
        for i in range(self.model_list.GetItemCount()):
            select.append(self.model_list.IsChecked(i))

        # Return the list.
        return select


    def set_selection(self, select):
        """Set the selection.

        @param select:  The list of selections.
        @type select:   list of bool
        """

        # Loop over the entries.
        for i in range(self.model_list.GetItemCount()):
            self.model_list.CheckItem(i, check=select[i])



class ModelSelListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.CheckListCtrlMixin):
    """A special list control with checkboxes."""

    def __init__(self, parent):
        """Initialise the control.

        @param parent:  The parent window.
        @type parent:   wx.Frame instance
        """

        # Execute the list control __init__() method.
        wx.ListCtrl.__init__(self, parent, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Execute the CheckListCtrlMixin __init__() method.
        wx.lib.mixins.listctrl.CheckListCtrlMixin.__init__(self)



class Protocol_mode_sel_window(wx.Dialog):
    """The protocol mode selector window object."""

    def __init__(self):
        """Set up the window."""

        # Set up the dialog.
        wx.Dialog.__init__(self, None, id=-1, title="Protocol mode selection")

        # Initialise some values
        size_x = 600
        size_y = 600
        border = 10
        self.select = 'Fully automated'

        # Set the frame properties.
        self.SetSize((size_x, size_y))
        self.Centre()
        self.SetFont(font.normal)

        # The main box sizer.
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Pack the sizer into the frame.
        self.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=border, packing=wx.HORIZONTAL)

        # Build the automatic part.
        self.build_auto(sizer)

        # Line separator.
        sizer.Add(wx.StaticLine(self, -1, style=wx.LI_VERTICAL), 0, wx.EXPAND|wx.ALL, border)

        # Build the manual part.
        self.build_manual(sizer)


    def build_auto(self, sizer):
        """Build the fully automated part of the window.

        @param sizer:   The sizer to pack the elements into.
        @type sizer:    wx.BoxSizer instance
        """

        # Create a vertical sizer for the elements.
        sub_sizer = wx.BoxSizer(wx.VERTICAL)

        # The title.
        title = wx.StaticText(self, -1, "Fully automated")
        title.SetFont(font.subtitle)
        sub_sizer.Add(title, 0, wx.ALIGN_CENTRE_HORIZONTAL, 0)

        # Spacing.
        sub_sizer.AddStretchSpacer()

        # The button.
        button = wx.BitmapButton(self, -1, wx.Bitmap(paths.icon_48x48.go_bottom, wx.BITMAP_TYPE_ANY))
        button.SetMinSize((80, 80))
        button.SetToolTipString("Perform a fully automated analysis, looping over global models I to V and terminating with the final run.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 3, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_full_analysis, button)

        # Spacing.
        sub_sizer.AddStretchSpacer()

        # Add the sub-sizer.
        sizer.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)


    def build_manual(self, sizer):
        """Build the manual part of the window.

        @param sizer:   The sizer to pack the elements into.
        @type sizer:    wx.BoxSizer instance
        """

        # Create a vertical sizer for the elements.
        sub_sizer = wx.BoxSizer(wx.VERTICAL)

        # The title.
        title = wx.StaticText(self, -1, "Manual modes")
        title.SetFont(font.subtitle)
        sub_sizer.Add(title, 0, wx.ALIGN_CENTRE_HORIZONTAL, 0)

        # Spacing.
        sub_sizer.AddSpacer(10)

        # The local_tm button.
        button = wx.Button(self, -1, u"Local \u03C4m")
        button.SetToolTipString("Optimise global model I, the local tm models.  Please click on the 'About' button for more information.")
        button.SetFont(font.normal)
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_local_tm, button)

        # The sphere button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Sphere"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'sphere.png', wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Optimise global model II, the spherical diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_sphere, button)

        # The prolate spheroid button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Prolate spheroid"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'prolate.png', wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Optimise global model III, the prolate spheroid diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_prolate, button)

        # The oblate spheroid button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Oblate spheroid"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'oblate.png', wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Optimise global model IV, the oblate spheroid diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_oblate, button)

        # The ellipsoid button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Ellipsoid"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'ellipsoid.png', wx.BITMAP_TYPE_ANY))
        button.SetFont(font.normal)
        button.SetToolTipString("Optimise global model V, the ellipsoid diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_ellipsoid, button)

        # The final button.
        button = wx.Button(self, -1, str_to_gui("Final"))
        button.SetToolTipString("The final run of the protocol.  Please click on the 'About' button for more information.")
        button.SetFont(font.normal)
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_final, button)

        # Add the sub-sizer.
        sizer.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)


    def select_ellipsoid(self, event=None):
        """The ellipsoid global model has been selected.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'ellipsoid'

        # Close the dialog.
        self.Close()


    def select_final(self, event=None):
        """The final stage of the protocol has been selected.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'final'

        # Close the dialog.
        self.Close()


    def select_full_analysis(self, event=None):
        """The full analysis has been selected.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'Fully automated'

        # Close the dialog.
        self.Close()


    def select_local_tm(self, event=None):
        """The local_tm global model has been selected.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'local_tm'

        # Close the dialog.
        self.Close()


    def select_prolate(self, event=None):
        """The prolate global model has been selected.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'prolate'

        # Close the dialog.
        self.Close()


    def select_oblate(self, event=None):
        """The oblate global model has been selected.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'oblate'

        # Close the dialog.
        self.Close()


    def select_sphere(self, event=None):
        """The sphere global model has been selected.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'sphere'

        # Close the dialog.
        self.Close()
