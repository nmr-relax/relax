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
from os import sep
import sys
import wx
import wx.lib.buttons
import wx.lib.mixins.listctrl

# relax module imports.
from auto_analyses import dauvergne_protocol
from data import Relax_data_store; ds = Relax_data_store()
from doc_builder import LIST, PARAGRAPH, SECTION, SUBSECTION, TITLE
from generic_fns.pipes import has_pipe
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from status import Status; status = Status()

# relax GUI module imports.
from gui.about import About_base
from gui.analyses.base import Base_analysis
from gui.analyses.execute import Execute
from gui.analyses.results_analysis import model_free_results, see_results
from gui.base_classes import Container
from gui.components.relax_data import Relax_data_list
from gui.controller import Redirect_text
from gui.filedialog import opendir
from gui.fonts import font
from gui.message import error_message, question, missing_data
from gui.misc import add_border, gui_to_int, gui_to_str, list_to_gui, protected_exec, str_to_gui
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



class Auto_model_free(Base_analysis):
    """The model-free auto-analysis GUI element."""

    def __init__(self, parent, id=-1, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=524288, name='scrolledpanel', gui=None, analysis_name=None, pipe_name=None, data_index=None):
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
        @keyword pipe_name:     The name of the data pipe associated with this analysis.
        @type pipe_name:        str
        @keyword data_index:    The index of the analysis in the relax data store (set to None if no data currently exists).
        @type data_index:       None or int
        """

        # Store the GUI main class.
        self.gui = gui

        # Init.
        self.init_flag = True

        # New data container.
        if data_index == None:
            # First create the data pipe if not already in existence (if this fails, then no data is set up).
            if not has_pipe(pipe_name) and not protected_exec(self.gui.interpreter.pipe.create, pipe_name, 'mf'):
                self.init_flag = False
                return

            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add('model-free')

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].grid_inc = None
            ds.relax_gui.analyses[data_index].mc_sim_num = None
            ds.relax_gui.analyses[data_index].save_dir = self.gui.launch_dir
            ds.relax_gui.analyses[data_index].local_tm_models = ['tm0', 'tm1', 'tm2', 'tm3', 'tm4', 'tm5', 'tm6', 'tm7', 'tm8', 'tm9']
            ds.relax_gui.analyses[data_index].mf_models = ['m0', 'm1', 'm2', 'm3', 'm4', 'm5', 'm6', 'm7', 'm8', 'm9']
            ds.relax_gui.analyses[data_index].max_iter = "30"
            ds.relax_gui.analyses[data_index].results_list = []

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
        status.observers.gui_uf.register(self.data.pipe_name, self.update_spin_count)

        # Execute the base class method to build the panel.
        super(Auto_model_free, self).__init__(parent, id=id, pos=pos, size=size, style=style, name=name)


    def _about(self, event):
        """The about window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the dialog.
        dialog = About_window(self)

        # Show the dialog.
        if status.show_gui:
            dialog.Show()


    def add_max_iterations(self, box):
        """Create and add the model-free maximum interation GUI element to the given box.

        @param box:     The box element to pack the model-free maximum iteration GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Sizer.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Text.
        label_maxiter = wx.StaticText(self, -1, "Maximum interations")
        label_maxiter.SetMinSize((240, 17))
        label_maxiter.SetFont(font.normal)
        sizer.Add(label_maxiter, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spinner.
        self.max_iter = wx.SpinCtrl(self, -1, self.data.max_iter, min=25, max=100)
        sizer.Add(self.max_iter, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

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

        # The pipe name.
        data.pipe_name = self.data.pipe_name

        # The model-free models (do not change these unless absolutely necessary).
        data.local_tm_models = self.local_tm_model_field.GetValue()
        data.mf_models = self.mf_model_field.GetValue()

        # Automatic looping over all rounds until convergence (must be a boolean value of True or False).
        data.conv_loop = True

        # Increment size.
        data.inc = gui_to_int(self.grid_inc.GetValue())

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

        # Spin vars.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if the bond length has been set.
            if not hasattr(spin, 'r') or spin.r == None:
                missing.append("Bond length data for spin '%s'." % spin_id)

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                missing.append("CSA data for spin '%s'." % spin_id)

            # Test if the heteronucleus type has been set.
            if not hasattr(spin, 'heteronuc_type') or spin.heteronuc_type == None:
                missing.append("Heteronucleus type data for spin '%s'." % spin_id)

            # Test if the proton type has been set.
            if not hasattr(spin, 'proton_type') or spin.proton_type == None:
                missing.append("Proton type data for spin '%s'." % spin_id)

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
            bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(bitmaps[i], wx.BITMAP_TYPE_ANY))

            # Add it.
            left_box.Add(bitmap, 0, wx.ALL, 0)

        # A spacer.
        left_box.AddStretchSpacer()

        # A button sizer, with some initial spacing.
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # An about button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, "About")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.about, wx.BITMAP_TYPE_ANY))
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
        self.add_text_sel_element(box, self, text="The data pipe:", default=self.data.pipe_name, tooltip="This is the data pipe associated with this analysis.", editable=False)

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self, text="Results directory", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, fn=self.results_directory, button=True)

        # Add the spin GUI element.
        self.add_spin_systems(box, self)

        # Add the relaxation data list GUI element, with spacing.
        box.AddSpacer(10)
        self.relax_data = Relax_data_list(gui=self.gui, parent=self, box=box, id=str(self.data_index))
        box.AddSpacer(10)

        # Add the local tau_m models GUI element, with spacing.
        self.local_tm_model_field = Local_tm_list(self, box)
        self.local_tm_model_field.SetValue(self.data.local_tm_models)

        # Add the model-free models GUI element, with spacing.
        self.mf_model_field = Mf_list(self, box)
        self.mf_model_field.SetValue(self.data.mf_models)

        # The optimisation settings.
        self.grid_inc = self.add_spin_element(box, self, text="Grid search increments:", default=11, min=1, max=100, tooltip="This is the number of increments per dimension of the grid search performed prior to numerical optimisation.")
        self.mc_sim_num = self.add_spin_element(box, self, text="Monte Carlo simulation number:", default=500, min=1, max=100000, tooltip="This is the number of Monte Carlo simulations performed for error propagation and analysis.")

        # Add maximum iteration selector.
        self.max_iter = self.add_spin_element(box, self, text="Maximum interations", default=str(self.data.max_iter), min=25, max=100)

        # The calculation mode.
        self.mode = self.add_text_sel_element(box, self, text="Protocol mode:", default='Fully automated', tooltip="Select if the dauvergne_protocol analysis will be fully automated or whether the individual global models will be optimised one by one.", icon=paths.icon_16x16.system_run, fn=self.mode_dialog, editable=False, button=True)

        # Stretchable spacing (with a minimal space).
        box.AddSpacer(30)
        box.AddStretchSpacer()

        # Add the execution GUI element.
        self.button_exec_id = self.add_execute_relax(box, self.execute)

        # Return the box.
        return box


    def delete(self):
        """Unregister the spin count from the user functions."""

        # Clean up the peak intensity object.
        self.peak_intensity.delete()

        # Remove.
        status.observers.gui_uf.unregister(self.data.pipe_name)


    def execute(self, event):
        """Set up, execute, and process the automatic model-free protocol.

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

        # Get the mode.
        mode = gui_to_str(self.mode.GetValue())

        # Solve for all global models.
        if mode == 'Fully automated':
            # The global model list.
            data.global_models = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid', 'final']

        # Any global model selected.
        else:
            data.global_models = [mode]

        # Display the relax controller (if not debugging).
        if not status.debug and status.show_gui:
            self.gui.controller.Show()

        # Threading flag.
        thread = True
        if status.debug:
            thread = False

        # Start the thread.
        self.thread = Execute_mf(self.gui, data, self.data_index, thread=thread)
        self.thread.start()

        # Terminate the event.
        event.Skip()


    def mode_dialog(self, event):
        """The calculation mode selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Show the model selector window.
        if status.show_gui:
            self.mode_win.ShowModal()

        # Set the model.
        self.mode.SetValue(str_to_gui(self.mode_win.select))


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
        """Synchronise the analysis frame and the relax data store, both ways.

        This method allows the frame information to be uploaded into the relax data store, or for the information in the relax data store to be downloaded by the frame.

        @keyword upload:    A flag which if True will cause the frame to send data to the relax data store.  If False, data will be downloaded from the relax data store to update the frame.
        @type upload:       bool
        """

        # The local tau_m models to use.
        if upload:
            self.data.local_tm_models = self.local_tm_model_field.GetValue()
        else:
            self.local_tm_model_field.SetValue(self.data.local_tm_models)

        # The model-free models to use.
        if upload:
            self.data.mf_models = self.mf_model_field.GetValue()
        else:
            self.mf_model_field.SetValue(self.data.mf_models)

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
            self.field_results_dir.SetValue(str(self.data.save_dir))

        # Maximum iterations.
        if upload:
            self.data.max_iter = gui_to_int(self.max_iter.GetValue())
        else:
            self.max_iter.SetValue(int(self.data.max_iter))



class Execute_mf(Execute):
    """The model-free analysis execution object."""

    def run_analysis(self):
        """Execute the calculation."""

        # Controller.
        if not status.debug and not status.test_mode:
            # Redirect relax output and errors to the controller.
            redir = Redirect_text(self.gui.controller)
            sys.stdout = redir
            sys.stderr = redir

        # Loop over the models.
        for global_model in self.data.global_models:
            # Start the protocol.
            dauvergne_protocol.dAuvergne_protocol(pipe_name=self.data.pipe_name, results_dir=self.data.save_dir, diff_model=global_model, mf_models=self.data.mf_models, local_tm_models=self.data.local_tm_models, grid_inc=self.data.inc, mc_sim_num=self.data.mc_sim_num, max_iter=self.data.max_iter, conv_loop=self.data.conv_loop)

            # Create the results file.
            if global_model == 'final':
                # Alias the relax data store data.
                data = ds.relax_gui.analyses[self.data_index]

                # Is there a results list (old results file support)?
                if not hasattr(data, 'results_list'):
                    data.results_list = []

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


    def SetValue(self, value):
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


    def modify(self, event):
        """Modify the model-free model selection.

        @param event:   The wx event.
        @type event:    wx event
        """

        # First state that this should not be done.
        msg = "The model-free models used in dauvergne_protocol auto-analysis should almost never be changed!  The consequences will be unpredictable.  Please proceed only if you are sure of what you are doing.  Would you like to modify the model-free model list?"
        if not question(msg, caption="Warning - do not change!", default=False):
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

        # Bind some events.
        self.Bind(wx.EVT_CLOSE, self.handler_close)


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


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Close the window.
        self.Hide()


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
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_local_tm, button)

        # The sphere button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Sphere"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'sphere.jpg', wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Optimise global model II, the spherical diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_sphere, button)

        # The prolate spheroid button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Prolate spheroid"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'prolate.jpg', wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Optimise global model III, the prolate spheroid diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_prolate, button)

        # The oblate spheroid button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Oblate spheroid"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'oblate.jpg', wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Optimise global model IV, the oblate spheroid diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_oblate, button)

        # The ellipsoid button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self, -1, None, str_to_gui("   Ellipsoid"))
        button.SetBitmapLabel(wx.Bitmap(paths.IMAGE_PATH+'ellipsoid.jpg', wx.BITMAP_TYPE_ANY))
        button.SetToolTipString("Optimise global model V, the ellipsoid diffusion model.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_ellipsoid, button)

        # The final button.
        button = wx.Button(self, -1, str_to_gui("Final"))
        button.SetToolTipString("The final run of the protocol.  Please click on the 'About' button for more information.")
        sub_sizer.Add(button, 1, wx.EXPAND, 0)
        self.Bind(wx.EVT_BUTTON, self.select_final, button)

        # Add the sub-sizer.
        sizer.Add(sub_sizer, 1, wx.ALL|wx.EXPAND, 0)


    def select_ellipsoid(self, event):
        """The ellipsoid global model has been selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'ellipsoid'

        # Close the dialog.
        self.Close()


    def select_final(self, event):
        """The final stage of the protocol has been selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'final'

        # Close the dialog.
        self.Close()


    def select_full_analysis(self, event):
        """The full analysis has been selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'Fully automated'

        # Close the dialog.
        self.Close()


    def select_local_tm(self, event):
        """The local_tm global model has been selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'local_tm'

        # Close the dialog.
        self.Close()


    def select_prolate(self, event):
        """The prolate global model has been selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'prolate'

        # Close the dialog.
        self.Close()


    def select_oblate(self, event):
        """The oblate global model has been selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'oblate'

        # Close the dialog.
        self.Close()


    def select_sphere(self, event):
        """The sphere global model has been selected.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the value.
        self.select = 'sphere'

        # Close the dialog.
        self.Close()
