###############################################################################
#                                                                             #
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

# Package docstring.
"""Package for the automatic and custom analysis GUI elements."""

# Python module imports.
import wx

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()

# relax GUI module imports.
from gui.analyses.auto_model_free import Auto_model_free
from gui.analyses.auto_noe import Auto_noe
from gui.analyses.auto_r1 import Auto_r1
from gui.analyses.auto_r2 import Auto_r2
from gui.analyses.results import Results_viewer
from gui.analyses.wizard import Analysis_wizard
from gui.message import question


# The package contents.
__all__ = ['auto_model_free',
           'auto_noe',
           'auto_r1',
           'auto_r2',
           'auto_rx_base',
           'base',
           'relax_control',
           'results_analysis',
           'results',
           'select_model_calc']


class Analysis_controller:
    """Class for controlling all aspects of analyses."""

    def __init__(self, gui):
        """Initialise the analysis controller.

        @param gui:         The gui object.
        @type gui:          wx object
        """

        # Store the args.
        self.gui = gui

        # Initialise some variables.
        self.init_state = True
        self._current = None
        self._num_analyses = 0

        # The analyses page objects.
        self.analyses = []


    def analysis_data_loop(self):
        """Loop over the analyses, yielding the data objects.

        @return:    The analysis data object from the relax data store.
        @rtype:     data.gui.Analyses instance
        """

        # Loop over the analyses.
        for i in range(self._num_analyses):
            yield ds.relax_gui.analyses[i]


    def analysis_loop(self):
        """Loop over the analyses, yielding the page objects.

        @return:    The page object.
        @rtype:     wx.Frame object
        """

        # Loop over the analyses.
        for i in range(self._num_analyses):
            yield self.analyses[i]


    def current_analysis_name(self):
        """Return the name of the current analysis.

        @return:    The name of the current analysis.
        @rtype:     str
        """

        # No current page.
        if self._current == None:
            return

        # Return the name.
        return self.analyses[self._current]


    def delete_all(self):
        """Remove all analyses."""

        # Delete the current tabs.
        while self._num_analyses:
            # Remove the last analysis, until there is nothing left.
            self.delete_analysis(self._num_analyses-1)


    def delete_analysis(self, index):
        """Delete the analysis tab and data store corresponding to the index.

        @param index:   The index of the analysis to delete.
        @type index:    int
        """

        # Delete the data store object.
        ds.relax_gui.analyses.pop(index)

        # Delete the tab.
        self.notebook.DeletePage(index)

        # Delete the tab object.
        self.analyses.pop(index)

        # Decrement the number of analyses.
        self._num_analyses -= 1

        # The current page has been deleted, so switch one back.
        if index == self._current:
            # Decrement.
            self._current -= 1

            # Switch to that page.
            self.notebook.SetSelection(self._current)


        # No more analyses, so in the initial state.
        if self._num_analyses == 0:
            # Reset the flag.
            self.init_state = True
            self._current = None

            # Delete the previous sizer.
            old_sizer = self.GetSizer()
            old_sizer.DeleteWindows()

            # Recreate the start screen.
            self.add_start_screen()


    def get_page_from_name(self, name):
        """Return the page corresponding to the given name.

        @return:    The page which matches the given name, or nothing otherwise.
        @rtype:     wx.Frame object or None
        """

        # Determine the analysis index.
        found = False
        for index in range(self._num_analyses):
            # Match.
            if name == ds.relax_gui.analyses[index].analysis_name:
                found = True
                break

        # No analysis found, so return nothing.
        if not found:
            return

        # Return the analysis page.
        return ds.relax_gui.analyses[index]


    def load_from_store(self):
        """Recreate the analyses from the relax data store."""

        map = {'NOE': 'noe',
               'R1': 'r1',
               'R2': 'r2',
               'model-free': 'mf'}
        for i in range(len(ds.relax_gui.analyses)):
            # The analysis name.
            if hasattr(ds.relax_gui.analyses[i], 'analysis_name'):
                analysis_name = ds.relax_gui.analyses[i].analysis_name
            elif ds.relax_gui.analyses[i].analysis_type == 'NOE':
                analysis_name = 'Steady-state NOE'
            elif ds.relax_gui.analyses[i].analysis_type == 'R1':
                analysis_name = 'R1 relaxation'
            elif ds.relax_gui.analyses[i].analysis_type == 'R2':
                analysis_name = 'R2 relaxation'
            elif ds.relax_gui.analyses[i].analysis_type == 'model-free':
                analysis_name = 'Model-free'

            # Set up the analysis.
            self.new_analysis(map[ds.relax_gui.analyses[i].analysis_type], analysis_name, index=i)


    def menu_close(self, event):
        """Close the currently opened analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Get the current analysis index.
        index = self.notebook.GetSelection()

        # Ask if this should be done.
        msg = "Are you sure you would like to close the current %s analysis tab?" % ds.relax_gui.analyses[index].analysis_type
        if not question(msg, default=False):
            return

        # Delete.
        self.delete_analysis(index)


    def menu_new(self, event):
        """Launch a wizard to select the new analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Initialise the analysis wizard, and obtain the user specified data.
        self.new_wizard = Analysis_wizard()
        data = self.new_wizard.run()

        # Failure, so do nothing.
        if data == None:
            return

        # Unpack the data.
        analysis_type, analysis_name, pipe_name = data

        # Initialise the new analysis.
        self.new_analysis(analysis_type, analysis_name, pipe_name)

        # Delete the wizard data.
        del self.new_wizard


    def new_analysis(self, analysis_type=None, analysis_name=None, pipe_name=None, index=None):
        """Initialise a new analysis.

        @keyword analysis_type: The type of analysis to initialise.  This can be one of 'noe', 'r1', 'r2', or 'mf'.
        @type analysis_type:    str
        @keyword analysis_name: The name of the analysis to initialise.
        @type analysis_name:    str
        @keyword index:         The index of the analysis in the relax data store (set to None if no data currently exists).
        @type index:            None or int
        """

        # Starting from the initial state.
        if self.init_state:
            # A new sizer for the notebook (to replace the current sizer).
            sizer = wx.BoxSizer(wx.VERTICAL)

            # Create a notebook and add it to the sizer.
            self.notebook = wx.Notebook(self.gui, -1, style=wx.NB_TOP)
            sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 0)

            # Delete the previous sizer.
            old_sizer = self.gui.GetSizer()
            old_sizer.DeleteWindows()

            # Add the new sizer to the main window.
            self.gui.SetSizer(sizer)
            sizer.Layout()

            # Set the flag.
            self.init_state = False

        # The analysis classes.
        classes = {'noe': Auto_noe,
                   'r1':  Auto_r1,
                   'r2':  Auto_r2,
                   'mf':  Auto_model_free}

        # Bad analysis type.
        if analysis_type not in classes.keys():
            raise RelaxError("The analysis '%s' is unknown." % analysis_type)

        # Get the class.
        analysis = classes[analysis_type]

        # Initialise the class and append it to the analysis window object.
        self.analyses.append(analysis(gui=self.gui, notebook=self.notebook, analysis_name=analysis_name, pipe_name=pipe_name, data_index=index))

        # Add to the notebook.
        self.notebook.AddPage(self.analyses[-1].parent, analysis_name)

        # Increment the number of analyses.
        self._num_analyses += 1

        # Set this new analysis to the current one.
        self._current = self._num_analyses - 1

        # Switch to the new page.
        self.notebook.SetSelection(self._current)

        # Reset the main window layout.
        self.gui.Layout()


    def show_results_viewer(self, event):
        """Display the analysis results.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Build the results viewer window.
        if not hasattr(self, 'results_viewer'):
            self.results_viewer = Results_viewer(gui=self.gui)

        # Open the window.
        self.results_viewer.Show()
