###############################################################################
#                                                                             #
# Copyright (C) 2010-2012 Edward d'Auvergne                                   #
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
import inspect
import sys
import wx
from types import ListType

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
import dep_check
from generic_fns import pipes
from status import Status; status = Status()

# relax GUI module imports.
from gui.analyses.auto_model_free import Auto_model_free
from gui.analyses.auto_noe import Auto_noe
from gui.analyses.auto_r1 import Auto_r1
from gui.analyses.auto_r2 import Auto_r2
from gui.analyses.wizard import Analysis_wizard
from gui.message import error_message, Question


# The package contents.
__all__ = ['auto_model_free',
           'auto_noe',
           'auto_r1',
           'auto_r2',
           'auto_rx_base',
           'base',
           'elements',
           'relax_control',
           'results_analysis',
           'results']


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
        self._switch_flag = True

        # The analyses page objects.
        self._analyses = []

        # Register the page switch method for pipe switches.
        self.name = 'notebook page switcher'
        status.observers.pipe_alteration.register(self.name, self.pipe_switch)

        # Register a method for removing analyses if the associated pipe is deleted.
        status.observers.pipe_alteration.register('notebook pipe deletion', self.pipe_deletion)

        # Register the deletion of all analyses for the reset status observer.
        status.observers.reset.register('gui analyses', self.post_reset)


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
            yield self._analyses[i]


    def current_data(self):
        """Return the data container of the current analysis from the relax data store.

        @return:    The data container of the current analysis.
        @rtype:     str
        """

        # No current page.
        if self._current == None:
            return

        # Return the name.
        return ds.relax_gui.analyses[self._current]


    def current_analysis_name(self):
        """Return the name of the current analysis.

        @return:    The name of the current analysis.
        @rtype:     str
        """

        # No current page.
        if self._current == None:
            return

        # Return the name.
        return ds.relax_gui.analyses[self._current].analysis_name


    def current_analysis_type(self):
        """Return the type of the current analysis.

        @return:    The type of the current analysis.
        @rtype:     str
        """

        # No current page.
        if self._current == None:
            return

        # Return the name.
        return ds.relax_gui.analyses[self._current].analysis_type


    def delete_all(self):
        """Remove all analyses."""

        # Delete the current tabs.
        while self._num_analyses:
            # Flush all pending events (bug fix for MS Windows).
            wx.Yield()

            # Remove the last analysis, until there is nothing left.
            self.delete_analysis(self._num_analyses-1)

        # Notify the observers of the change.
        status.observers.gui_analysis.notify()


    def delete_analysis(self, index):
        """Delete the analysis tab and data store corresponding to the index.

        The order of these operations is very important due to the notification of observer objects and the updates, synchronisations, etc. that follow.  If the program debugging mode is on, then print outs at each stage will occur to allow the following of the code and observer object notifications.


        @param index:   The index of the analysis to delete.
        @type index:    int
        """

        # Debugging set up.
        if status.debug:
            fn_name = sys._getframe().f_code.co_name
            mod_name = inspect.getmodule(inspect.stack()[1][0]).__name__
            class_name = self.__class__.__name__
            full_name = "%s.%s.%s" % (mod_name, class_name, fn_name)
            print("\n\n")
            print("debug> %s:  Deleting the analysis at index %s." % (full_name, index))

        # Decrement the number of analyses.
        self._num_analyses -= 1

        # Shift the current page back one if necessary.
        if self._current > index:
            self._current -= 1
            if status.debug:
                print("debug> %s:  Switching the current analysis to index %s." % (full_name, self._current))

        # Execute the analysis delete method, if it exists.
        if hasattr(self._analyses[index], 'delete'):
            if status.debug:
                print("debug> %s:  Executing the analysis specific delete() method." % full_name)
            self._analyses[index].delete()

        # Delete the tab.
        if status.debug:
            print("debug> %s:  Deleting the notebook page." % full_name)
        self.notebook.DeletePage(index)

        # Delete the tab object.
        if status.debug:
            print("debug> %s:  Deleting the analysis GUI object." % full_name)
        self._analyses.pop(index)

        # The current page has been deleted, so switch one back (if possible).
        if index == self._current and self._current != 0:
            if status.debug:
                print("debug> %s:  Switching to page %s." % (full_name, self._current-1))
            self.switch_page(self._current-1)

        # No more analyses, so in the initial state.
        if self._num_analyses == 0:
            if status.debug:
                print("debug> %s:  Setting the initial state." % full_name)
            self.set_init_state()

        # Notify the observers of the change.
        status.observers.gui_analysis.notify()

        # Store the pipe name.
        pipe_name = ds.relax_gui.analyses[index].pipe_name

        # Delete the data store object.
        if status.debug:
            print("debug> %s:  Deleting the data store object." % full_name)
        ds.relax_gui.analyses.pop(index)

        # Delete all data pipes associated with the analysis.
        if pipes.has_pipe(pipe_name):
            if status.debug:
                print("debug> %s:  Deleting the data pipe '%s'." % (full_name, pipe_name))
            pipes.delete(pipe_name)


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
        return self._analyses[index]


    def load_from_store(self):
        """Recreate the analyses from the relax data store."""

        # No relax_gui data store structure, so do nothing.
        if not hasattr(ds, 'relax_gui'):
            return

        # A remapping table.
        map = {'NOE': 'noe',
               'R1': 'r1',
               'R2': 'r2',
               'model-free': 'mf'}

        # Loop over each analysis.
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
            self._switch_flag = False
            self.new_analysis(map[ds.relax_gui.analyses[i].analysis_type], analysis_name, index=i)

        # Switch to the page of the current data pipe.
        self.pipe_switch()

        # Reset the switching flag.
        self._switch_flag = True

        # Notify the observers of the change.
        status.observers.gui_analysis.notify()


    def menu_close(self, event):
        """Close the currently opened analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Notebook not created yet, so skip.
        if not hasattr(self, 'notebook'):
            return

        # Execution lock.
        if status.exec_lock.locked():
            return

        # Get the current analysis index.
        index = self.notebook.GetSelection()

        # Ask if this should be done.
        msg = "Are you sure you would like to close the current %s analysis tab?" % ds.relax_gui.analyses[index].analysis_type
        if status.show_gui and Question(msg, title="Close current analysis", size=(350, 140), default=False).ShowModal() == wx.ID_NO:
            return

        # Delete.
        self.delete_analysis(index)


    def menu_close_all(self, event):
        """Close all analyses.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Notebook not created yet, so skip.
        if not hasattr(self, 'notebook'):
            return

        # Execution lock.
        if status.exec_lock.locked():
            return

        # Ask if this should be done.
        msg = "Are you sure you would like to close all analyses?  All data will be erased and the relax data store reset."
        if status.show_gui and Question(msg, title="Close all analyses", size=(350, 150), default=False).ShowModal() == wx.ID_NO:
            return

        # Delete.
        self.delete_all()


    def menu_new(self, event):
        """Launch a wizard to select the new analysis.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execution lock.
        if status.exec_lock.locked():
            return

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

        # Check the C modules.
        if analysis_type in ['r1', 'r2'] and not dep_check.C_module_exp_fn:
            error_message("Relaxation curve fitting is not available.  Try compiling the C modules on your platform.")
            return

        # Freeze the GUI.
        wx.Yield()
        wx.BeginBusyCursor()
        self.gui.Freeze()

        # Starting from the initial state.
        if self.init_state:
            # A new sizer for the notebook (to replace the current sizer).
            sizer = wx.BoxSizer(wx.VERTICAL)

            # Create a notebook and add it to the sizer.
            self.notebook = wx.Notebook(self.gui, -1, style=wx.NB_TOP)
            sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 0)

            # Bind changing events.
            self.gui.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self.on_page_changing)
            self.gui.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_page_changed)

            # Delete the previous sizer.
            old_sizer = self.gui.GetSizer()
            old_sizer.DeleteWindows()

            # Add the new sizer to the main window.
            self.gui.SetSizer(sizer)
            sizer.Layout()

        # The analysis classes.
        classes = {'noe': Auto_noe,
                   'r1':  Auto_r1,
                   'r2':  Auto_r2,
                   'mf':  Auto_model_free}

        # Bad analysis type.
        if analysis_type not in classes.keys():
            raise RelaxError("The analysis '%s' is unknown." % analysis_type)

        # Initialise the class.
        analysis = classes[analysis_type](parent=self.notebook, id=-1, gui=self.gui, analysis_name=analysis_name, pipe_name=pipe_name, data_index=index)

        # Failure.
        if not analysis.init_flag:
            # Reset.
            if self.init_state:
                self.set_init_state()

            # Stop operation.
            return

        # Append the class object to the analysis window object.
        self._analyses.append(analysis)

        # Add to the notebook.
        self.notebook.AddPage(self._analyses[-1], analysis_name)

        # Increment the number of analyses.
        self._num_analyses += 1

        # Switch to the new page.
        if self._switch_flag:
            self.switch_page(self._num_analyses-1)

        # Set the initialisation flag.
        self.init_state = False

        # Reset the main window layout.
        self.gui.Layout()

        # Thaw the GUI.
        self.gui.Thaw()
        if wx.IsBusy():
            wx.EndBusyCursor()

        # Notify the observers of the change.
        status.observers.gui_analysis.notify()


    def on_page_changing(self, event):
        """Block page changing if needed.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Execution lock.
        if status.exec_lock.locked():
            # Show an error message.
            error_message("Cannot change analyses, relax is currently executing.", "relax execution lock")

            # Veto the event.
            event.Veto()


    def on_page_changed(self, event):
        """Handle page changes.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The index.
        self._current = event.GetSelection()

        # Switch to the major data pipe of that page if not the current one.
        if self._switch_flag and pipes.cdp_name() != ds.relax_gui.analyses[self._current].pipe_name:
            self.gui.interpreter.apply('pipe.switch', ds.relax_gui.analyses[self._current].pipe_name)

        # Normal operation.
        event.Skip()

        # Notify the observers of the change.
        status.observers.gui_analysis.notify()


    def page_index_from_pipe(self, pipe):
        """Find the page holding the data pipe and return its page index.

        @param pipe:    The data pipe to find the page of.
        @type pipe:     str
        @return:        The page index.
        @rtype:         int or None
        """

        # Find the index.
        index = None
        for i in range(self._num_analyses):
            # Matching page.
            if ds.relax_gui.analyses[i].pipe_name == pipe:
                index = i
                break

        # Return the index.
        return index


    def page_name_from_pipe(self, pipe):
        """Find the page holding the data pipe and return its name.

        @param pipe:    The data pipe to find the page of.
        @type pipe:     str
        @return:        The page name.
        @rtype:         str or None
        """

        # Find the index.
        index = self.page_index_from_pipe(pipe)

        # No matching page.
        if index == None:
            return

        # Return the page name.
        return ds.relax_gui.analyses[index].analysis_name


    def pipe_deletion(self):
        """Remove analysis tabs for which the associated data pipe has been deleted."""

        # Loop over the analyses, noting which no longer have a data pipe.
        del_list = []
        for i in range(self._num_analyses):
            if not pipes.has_pipe(ds.relax_gui.analyses[i].pipe_name):
                del_list.append(i)

        # Reverse the order of the list so the removal works correctly.
        del_list.reverse()

        # Delete the analyses.
        for index in del_list:
            self.delete_analysis(index)


    def pipe_switch(self, pipe=None):
        """Switch the page to the given or current data pipe.

        @keyword pipe:  The pipe associated with the page to switch to.  If not supplied, the current data pipe will be used.
        @type pipe:     str or None
        """

        # The data pipe.
        if pipe == None:
            pipe = pipes.cdp_name()

        # Find the page.
        index = self.page_index_from_pipe(pipe)

        # No matching page.
        if index == None:
            return

        # The page is already active, so do nothing.
        if self._current == index:
            return

        # Switch to the page.
        self.switch_page(index)

        # Notify the observers of the change.
        status.observers.gui_analysis.notify()


    def post_reset(self):
        """Post relax data store reset event handler."""

        # Delete all tabs.
        while self._num_analyses:
            # The index of the tab to remove.
            index = self._num_analyses - 1

            # Delete the tab.
            self.notebook.DeletePage(index)

            # Delete the tab object.
            self._analyses.pop(index)

            # Decrement the number of analyses.
            self._num_analyses -= 1

            # Set the initial state.
            self.set_init_state()


    def set_init_state(self):
        """Revert to the initial state."""

        # Reset the flag.
        self.init_state = True
        self._current = None

        # Delete the previous sizer.
        old_sizer = self.gui.GetSizer()
        old_sizer.DeleteWindows()

        # Delete the notebook.
        del self.notebook

        # Recreate the start screen.
        self.gui.add_start_screen()


    def switch_page(self, index):
        """Switch to the given page.

        @param index:   The index of the page to switch to.
        @type index:    int
        """

        # Set the current page number.
        self._current = index

        # Switch to the page.
        wx.CallAfter(self.notebook.SetSelection, self._current)

        # Notify the observers of the change.
        wx.CallAfter(status.observers.gui_analysis.notify)
