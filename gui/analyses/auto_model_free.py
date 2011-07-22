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

# relax module imports.
from auto_analyses import dauvergne_protocol
from data import Relax_data_store; ds = Relax_data_store()
from doc_builder import LIST, PARAGRAPH, SECTION, SUBSECTION, TITLE
from generic_fns.pipes import has_pipe
from status import Status; status = Status()

# relax GUI module imports.
from gui.about import About_base
from gui.analyses.base import Base_frame
from gui.analyses.execute import Execute
from gui.analyses.results_analysis import model_free_results, see_results
from gui.analyses.select_model_calc import Select_tensor
from gui.base_classes import Container
from gui.components.relax_data import Relax_data_list
from gui.controller import Redirect_text
from gui.filedialog import opendir
from gui.message import error_message, missing_data
from gui.misc import add_border, gui_to_int, protected_exec
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
    def __init__(self, gui=None, notebook=None, analysis_name=None, pipe_name=None, data_index=None):
        """Build the automatic model-free protocol GUI element.

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
            # First create the data pipe if not already in existence (if this fails, then no data is set up).
            if not has_pipe(pipe_name) and not protected_exec(self.gui.interpreter.pipe.create, pipe_name, 'noe'):
                self.init_flag = False
                return

            # Generate a storage container in the relax data store, and alias it for easy access.
            data_index = ds.relax_gui.analyses.add('model-free')

            # Store the analysis and pipe names.
            ds.relax_gui.analyses[data_index].analysis_name = analysis_name
            ds.relax_gui.analyses[data_index].pipe_name = pipe_name

            # Initialise the variables.
            ds.relax_gui.analyses[data_index].model_toggle = [True]*10
            ds.relax_gui.analyses[data_index].grid_inc = None
            ds.relax_gui.analyses[data_index].mc_sim_num = None
            ds.relax_gui.analyses[data_index].save_dir = self.gui.launch_dir
            ds.relax_gui.analyses[data_index].max_iter = "30"
            ds.relax_gui.analyses[data_index].results_list = []

        # Alias the data.
        self.data = ds.relax_gui.analyses[data_index]
        self.data_index = data_index

        # The parent GUI element for this class.
        self.parent = wx.lib.scrolledpanel.ScrolledPanel(notebook, -1)

        # Pack a sizer into the panel.
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        self.parent.SetSizer(box_main)

        # Build the central sizer, with borders.
        box_centre = add_border(box_main, border=self.border, packing=wx.HORIZONTAL)

        # Build and pack the main sizer box, then add it to the automatic model-free analysis frame.
        self.build_main_box(box_centre)

        # Set up the scrolled panel.
        self.parent.SetAutoLayout(True)
        self.parent.SetupScrolling(scroll_x=False, scroll_y=True)

        # Register the method for updating the spin count for the completion of user functions.
        status.observers.gui_uf.register(self.data.pipe_name, self.update_spin_count)


    def _about(self, event):
        """The about window.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the dialog.
        dialog = About_window(self.parent)

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
        label_maxiter = wx.StaticText(self.parent, -1, "Maximum interations")
        label_maxiter.SetMinSize((240, 17))
        label_maxiter.SetFont(self.gui.font_normal)
        sizer.Add(label_maxiter, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Spinner.
        self.max_iter = wx.SpinCtrl(self.parent, -1, self.data.max_iter, min=25, max=100)
        sizer.Add(self.max_iter, 1, wx.ADJUST_MINSIZE|wx.ALIGN_CENTER_VERTICAL, 0)

        # Add the element to the box.
        box.Add(sizer, 0, wx.ALL|wx.EXPAND, 0)


    def add_mf_models(self, box):
        """Create and add the model-free model picking GUI element to the given box.

        @param box:     The box element to pack the model-free model picking GUI element into.
        @type box:      wx.BoxSizer instance
        """

        # Add a label.
        self.add_static_text(box, self.parent, "Select model-free models (default = all):")

        # Add some spacing.
        box.AddSpacer(5)

        # A horizontal sizer for the buttons.
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        # The help text.
        text = ["{}",
                "{S2}",
                "{S2, te}",
                "{S2, Rex}",
                "{S2, te, Rex}",
                "{S2, S2f, ts}",
                "{S2, tf, S2f, ts}",
                "{S2, S2f, ts, Rex}",
                "{S2, tf, S2f, ts, Rex}",
                "{Rex}"]

        # Loop over the 10 models.
        for i in range(10):
            # The model name.
            name = "m%s" % i

            # The button.
            setattr(self, name, wx.ToggleButton(self.parent, -1, name))

            # Get the button.
            button = getattr(self, name)

            # Set the properties.
            button.SetMinSize((-1, 25))
            button.SetFont(self.gui.font_button)
            button.SetToolTipString(text[i])

            # Default is on.
            button.SetValue(1)

            # Add the button.
            sizer.Add(button, 1, wx.ADJUST_MINSIZE, 0)

        # Add the title and buttons to the main box.
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
        data.mf_models = []
        data.local_tm_models = []
        for i in range(len(self.data.model_toggle)):
            if self.data.model_toggle[i]:
                data.mf_models.append('m%i' % i)
                data.local_tm_models.append('tm%i' % i)

        # A file containing a list of spins which can be dynamically excluded at any point within the analysis (when set to None, this variable is not used).
        data.exclude = None

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
            bitmap = wx.StaticBitmap(self.parent, -1, wx.Bitmap(bitmaps[i], wx.BITMAP_TYPE_ANY))

            # Add it.
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

        # Bottom spacer.
        left_box.AddSpacer(10)

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
        self.add_text_sel_element(box, self.parent, text="The data pipe:", default=self.data.pipe_name, tooltip="This is the data pipe associated with this analysis.", editable=False)

        # Add the results directory GUI element.
        self.field_results_dir = self.add_text_sel_element(box, self.parent, text="Results directory", icon=paths.icon_16x16.open_folder, default=self.data.save_dir, fn=self.results_directory, button=True)

        # Add the spin GUI element.
        self.add_spin_systems(box, self.parent)

        # Add the relaxation data list GUI element, with spacing.
        box.AddSpacer(10)
        self.relax_data = Relax_data_list(gui=self.gui, parent=self.parent, box=box, id=str(self.data_index))
        box.AddSpacer(10)

        # Add the model-free models GUI element, with spacing.
        self.add_mf_models(box)
        box.AddSpacer(10)

        # The optimisation settings.
        self.grid_inc = self.add_spin_element(box, self.parent, text="Grid search increments:", default=11, min=1, max=100, tooltip="This is the number of increments per dimension of the grid search performed prior to numerical optimisation.")
        self.mc_sim_num = self.add_spin_element(box, self.parent, text="Monte Carlo simulation number:", default=500, min=1, max=100000, tooltip="This is the number of Monte Carlo simulations performed for error propagation and analysis.")

        # Add maximum iteration selector.
        self.max_iter = self.add_spin_element(box, self.parent, text="Maximum interations", default=str(self.data.max_iter), min=25, max=100)

        # Some spacing.
        box.AddStretchSpacer()

        # Add the execution GUI element.
        self.button_exec_id = self.add_execute_relax(box, self.execute)

        # Return the box.
        return box


    def choose_global_model(self, local_tm_complete=False):
        """Select the individual global models to solve, or all automatically.

        @keyword local_tm_complete: A flag specifying if the local tm global model has been solved already.
        @type local_tm_complete:    bool
        @return:                    The global model selected, or 'full' for all.
        @rtype:                     str
        """

        # The dialog.
        dlg = Select_tensor(None, -1, "", local_tm_flag=True)
        if status.show_gui:
            dlg.ShowModal()

        # Return the choice.
        return dlg.selection


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

        # The global model.
        which_model = self.choose_global_model(False)

        # Cancel.
        if which_model == None:
            return

        # Solve for all global models.
        elif which_model == 'full':
            # The global model list.
            data.global_models = ['local_tm', 'sphere', 'prolate', 'oblate', 'ellipsoid', 'final']

        # Any global model selected.
        else:
            data.global_models = [which_model]

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
