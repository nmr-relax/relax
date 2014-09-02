###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2014 Edward d'Auvergne                                   #
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
"""Module containing the classes for GUI components involving spectral data."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from graphics import fetch_icon
from gui.components.base_list import Base_list
from gui.string_conv import float_to_gui, gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from lib.compat import u
from pipe_control.spectrum import replicated_flags, replicated_ids
from status import Status; status = Status()
from specific_analyses.relax_disp.data import is_cpmg_exp_type, is_r1rho_exp_type
from user_functions.data import Uf_info; uf_info = Uf_info()


class Spectra_list(Base_list):
    """The GUI element for listing loaded spectral data."""

    def __init__(self, gui=None, parent=None, box=None, id=None, fn_add=None, proportion=0, button_placement='default', noe_flag=False, relax_fit_flag=False, relax_disp_flag=False):
        """Build the spectral list GUI element.

        @keyword gui:               The main GUI object.
        @type gui:                  wx.Frame instance
        @keyword parent:            The parent GUI element that this is to be attached to (the panel object).
        @type parent:               wx object
        @keyword data:              The data storage container.
        @type data:                 class instance
        @keyword box:               The vertical box sizer to pack this GUI component into.
        @type box:                  wx.BoxSizer instance
        @keyword id:                A unique identification string.  This is used to register the update method with the GUI user function observer object.
        @type id:                   str
        @keyword fn_add:            The function to execute when clicking on the 'Add' button.
        @type fn_add:               func
        @keyword proportion:        The window proportion parameter.
        @type proportion:           bool
        @keyword button_placement:  Override the button visibility and placement.  The value of 'default' will leave the buttons at the default setting.  The value of 'top' will place the buttons at the top, 'bottom' will place them at the bottom, and None will turn off the buttons.
        @type button_placement:     str or None
        @keyword noe_flag:          A flag which when True will enable the steady-state NOE portions of the wizard.
        @type noe_flag:             bool
        @keyword relax_fit_flag:    A flag which when True will enable the relaxation curve-fitting portions of the wizard.
        @type relax_fit_flag:       bool
        @keyword relax_disp_flag:   A flag which when True will enable the relaxation dispersion portions of the wizard.
        @type relax_disp_flag:      bool
        """

        # Store the arguments.
        self.fn_add = fn_add
        self.noe_flag = noe_flag
        self.relax_fit_flag = relax_fit_flag
        self.relax_disp_flag = relax_disp_flag

        # Initialise the base class.
        super(Spectra_list, self).__init__(gui=gui, parent=parent, box=box, id=id, proportion=proportion, button_placement=button_placement)


    def action_relax_disp_cpmg_setup(self, event=None, item=None):
        """Launch the relax_disp.cpmg_setup user function.

        @keyword event: The wx event.
        @type event:    wx event
        @keyword item:  This is for debugging purposes only, to allow the GUI tests to select items without worrying about OS dependent wxPython bugs.
        @type item:     None or int
        """

        # The current selection.
        if item == None:
            item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current frequency.
        frq = None
        frq_flag = False
        if hasattr(cdp, 'cpmg_frqs') and id in cdp.cpmg_frqs.keys():
            frq = cdp.cpmg_frqs[id]
            frq_flag = True

        # The current ncyc_even flag.
        even = True
        even_flag = False
        if hasattr(cdp, 'ncyc_even') and id in cdp.ncyc_even.keys():
            even = cdp.ncyc_even[id]
            even_flag = True

        # Launch the dialog.
        if frq_flag:
            uf_store['relax_disp.cpmg_setup'](spectrum_id=id, cpmg_frq=frq, ncyc_even=even)
        else:
            uf_store['relax_disp.cpmg_setup'](spectrum_id=id, ncyc_even=even)


    def action_relax_disp_exp_type(self, event=None, item=None):
        """Launch the relax_disp.exp_type user function.

        @keyword event: The wx event.
        @type event:    wx event
        @keyword item:  This is for debugging purposes only, to allow the GUI tests to select items without worrying about OS dependent wxPython bugs.
        @type item:     None or int
        """

        # The current selection.
        if item == None:
            item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current type.
        exp_type = None
        if hasattr(cdp, 'exp_type') and id in cdp.exp_type.keys():
            exp_type = cdp.exp_type[id]

        # Launch the dialog.
        if exp_type == None:
            uf_store['relax_disp.exp_type'](spectrum_id=id)
        else:
            uf_store['relax_disp.exp_type'](spectrum_id=id, exp_type=exp_type)


    def action_relax_disp_relax_time(self, event=None, item=None):
        """Launch the relax_disp.relax_time user function.

        @keyword event: The wx event.
        @type event:    wx event
        @keyword item:  This is for debugging purposes only, to allow the GUI tests to select items without worrying about OS dependent wxPython bugs.
        @type item:     None or int
        """

        # The current selection.
        if item == None:
            item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current time.
        time = None
        if hasattr(cdp, 'relax_times') and id in cdp.relax_times.keys():
            time = cdp.relax_times[id]

        # Launch the dialog.
        if time == None:
            uf_store['relax_disp.relax_time'](spectrum_id=id)
        else:
            uf_store['relax_disp.relax_time'](time=time, spectrum_id=id)


    def action_relax_disp_spin_lock_field(self, event=None, item=None):
        """Launch the relax_disp.spin_lock_field user function.

        @keyword event: The wx event.
        @type event:    wx event
        @keyword item:  This is for debugging purposes only, to allow the GUI tests to select items without worrying about OS dependent wxPython bugs.
        @type item:     None or int
        """

        # The current selection.
        if item == None:
            item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The spin-lock.
        nu1 = None
        nu1_flag = False
        if hasattr(cdp, 'spin_lock_nu1') and id in cdp.spin_lock_nu1.keys():
            nu1 = cdp.spin_lock_nu1[id]
            nu1_flag = True

        # Launch the dialog.
        if nu1_flag:
            uf_store['relax_disp.spin_lock_field'](field=nu1, spectrum_id=id)
        else:
            uf_store['relax_disp.spin_lock_field'](spectrum_id=id)


    def action_relax_disp_spin_lock_offset(self, event=None, item=None):
        """Launch the relax_disp.spin_lock_offset user function.

        @keyword event: The wx event.
        @type event:    wx event
        @keyword item:  This is for debugging purposes only, to allow the GUI tests to select items without worrying about OS dependent wxPython bugs.
        @type item:     None or int
        """

        # The current selection.
        if item == None:
            item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The offset.
        offset = None
        offset_flag = False
        if hasattr(cdp, 'spin_lock_offset') and id in cdp.spin_lock_offset.keys():
            offset = cdp.spin_lock_offset[id]
            offset_flag = True

        # Launch the dialog.
        if offset_flag:
            uf_store['relax_disp.spin_lock_offset'](offset=offset, spectrum_id=id)
        else:
            uf_store['relax_disp.spin_lock_offset'](spectrum_id=id)


    def action_relax_fit_relax_time(self, event=None, item=None):
        """Launch the relax_fit.relax_time user function.

        @keyword event: The wx event.
        @type event:    wx event
        @keyword item:  This is for debugging purposes only, to allow the GUI tests to select items without worrying about OS dependent wxPython bugs.
        @type item:     None or int
        """

        # The current selection.
        if item == None:
            item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current time.
        time = None
        if hasattr(cdp, 'relax_times') and id in cdp.relax_times.keys():
            time = cdp.relax_times[id]

        # Launch the dialog.
        if time == None:
            uf_store['relax_fit.relax_time'](spectrum_id=id)
        else:
            uf_store['relax_fit.relax_time'](time=time, spectrum_id=id)


    def action_spectrometer_frq(self, event=None, item=None):
        """Launch the spectrometer.frequency user function.

        @keyword event: The wx event.
        @type event:    wx event
        @keyword item:  This is for debugging purposes only, to allow the GUI tests to select items without worrying about OS dependent wxPython bugs.
        @type item:     None or int
        """

        # The current selection.
        if item == None:
            item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current frequency.
        frq = None
        if hasattr(cdp, 'spectrometer_frq') and id in cdp.spectrometer_frq:
            frq = cdp.spectrometer_frq[id]

        # Launch the dialog.
        if frq == None:
            uf_store['spectrometer.frequency'](id=id)
        else:
            uf_store['spectrometer.frequency'](frq=frq, id=id)


    def action_spectrum_baseplane_rmsd(self, event):
        """Launch the spectrum.baseplane_rmsd user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # Launch the dialog.
        uf_store['spectrum.baseplane_rmsd'](spectrum_id=id)


    def action_spectrum_delete(self, event):
        """Launch the spectrum.delete user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # No selection.
        if item == -1:
            id = None

        # Selected item.
        else:
            # The spectrum ID.
            id = gui_to_str(self.element.GetItemText(item))

        # Launch the dialog.
        uf_store['spectrum.delete'](spectrum_id=id)


    def action_spectrum_error_analysis(self, event):
        """Launch the spectrum.error_analysis user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The first item selected.
        item = self.element.GetFirstSelected()

        # Loop over the additional selections.
        ids = []
        while 1:
            # No selection.
            if item == -1:
                break

            # Add the ID string to the list.
            ids.append(gui_to_str(self.element.GetItemText(item)))

            # Get the next selected item.
            item = self.element.GetNextSelected(item)

        # No selected items.
        if not len(ids):
            ids = None

        # Launch the dialog.
        uf_store['spectrum.error_analysis'](subset=ids, wx_wizard_modal=True)

        # Display the relax controller, and go to the end of the log window.
        self.gui.show_controller(None)
        self.gui.controller.log_panel.on_goto_end(None)


    def action_spectrum_integration_points(self, event):
        """Launch the spectrum.integration_points user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # Launch the dialog.
        uf_store['spectrum.integration_points'](spectrum_id=id)


    def action_spectrum_replicated(self, event):
        """Launch the spectrum.replicated user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current replicates.
        replicates = replicated_ids(id)

        # Launch the dialog.
        if replicates == []:
            uf_store['spectrum.replicated'](spectrum_ids=id)
        else:
            uf_store['spectrum.replicated'](spectrum_ids=replicates)


    def add_disp_point(self, index):
        """Add the dispersion point info to the element.

        This is either the CPMG pulse frequency or the spin-lock field strength.  Both share the same column.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if the data exists, False otherwise.
        @rtype:         bool
        """

        # Append a column.
        self.element.InsertColumn(index, u("\u03BDCPMG (Hz) or Spin-lock \u03BD1 (Hz)"))

        # No data.
        if not hasattr(cdp, 'spectrum_ids'):
            return True

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # Set the CPMG frequency.
            if hasattr(cdp, 'cpmg_frqs') and cdp.spectrum_ids[i] in cdp.cpmg_frqs.keys():
                self.element.SetStringItem(i, index, float_to_gui(cdp.cpmg_frqs[cdp.spectrum_ids[i]]))

            # Set the spin-lock field strength.
            if hasattr(cdp, 'spin_lock_nu1') and cdp.spectrum_ids[i] in cdp.spin_lock_nu1.keys():
                self.element.SetStringItem(i, index, float_to_gui(cdp.spin_lock_nu1[cdp.spectrum_ids[i]]))

        # Successful.
        return True


    def add_exp_type(self, index):
        """Add the experiment type info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if the data exists, False otherwise.
        @rtype:         bool
        """

        # Append a column.
        self.element.InsertColumn(index, u("Experiment type"))

        # No data.
        if not hasattr(cdp, 'spectrum_ids') or not hasattr(cdp, 'exp_type'):
            return True

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.exp_type.keys():
                continue

            # Set the value.
            self.element.SetStringItem(i, index, float_to_gui(cdp.exp_type[cdp.spectrum_ids[i]]))

        # Successful.
        return True


    def add_frqs(self, index):
        """Add the spectrometer frequency info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if the frequency data exists, False otherwise.
        @rtype:         bool
        """

        # Append a column.
        self.element.InsertColumn(index, u("\u03C9H (MHz)"))

        # No data.
        if not hasattr(cdp, 'spectrum_ids'):
            return True
        if not hasattr(cdp, 'spectrometer_frq') or not len(cdp.spectrometer_frq):
            return True

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.spectrometer_frq:
                continue

            # Set the value (in MHz).
            self.element.SetStringItem(i, index, float_to_gui(cdp.spectrometer_frq[cdp.spectrum_ids[i]]/1e6))

        # Successful.
        return True


    def add_offset(self, index):
        """Add the offset info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if the data exists, False otherwise.
        @rtype:         bool
        """

        # Append a column.
        self.element.InsertColumn(index, u("Offset \u03C9_rf (ppm)"))

        # No data.
        if not hasattr(cdp, 'spectrum_ids'):
            return True

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            if hasattr(cdp, 'spin_lock_offset') and cdp.spectrum_ids[i] in cdp.spin_lock_offset.keys():
                self.element.SetStringItem(i, index, float_to_gui(cdp.spin_lock_offset[cdp.spectrum_ids[i]]))

        # Successful.
        return True


    def generate_popup_menu(self, id=None):
        """Create the popup menu.

        @keyword id:    The spectrum ID string for the row that was clicked on.
        @type id:       str
        @return:        The popup menu.
        @rtype:         list of dict of wxID, str, str, method
        """

        # The right click popup menu.
        popup_menus = [
            {
                'id': wx.NewId(),
                'text': "Set the &baseplane RMSD",
                'icon': fetch_icon(uf_info.get_uf('spectrum.baseplane_rmsd').gui_icon),
                'method': self.action_spectrum_baseplane_rmsd
            }, {
                'id': wx.NewId(),
                'text': "&Delete the peak intensities",
                'icon': fetch_icon(uf_info.get_uf('spectrum.delete').gui_icon),
                'method': self.action_spectrum_delete
            }, {
                'id': wx.NewId(),
                'text': "Set the number of integration &points",
                'icon': fetch_icon(uf_info.get_uf('spectrum.integration_points').gui_icon),
                'method': self.action_spectrum_integration_points
            }, {
                'id': wx.NewId(),
                'text': "Specify which spectra are &replicated",
                'icon': fetch_icon(uf_info.get_uf('spectrum.replicated').gui_icon),
                'method': self.action_spectrum_replicated
            }
        ]
        if self.relax_disp_flag:
            popup_menus.append({
                'id': wx.NewId(),
                'text': "Set the &experiment type",
                'icon': None,
                'method': self.action_relax_disp_exp_type
            })
        if self.relax_fit_flag:
            popup_menus.append({
                'id': wx.NewId(),
                'text': "Set the relaxation &time",
                'icon': fetch_icon(uf_info.get_uf('relax_fit.relax_time').gui_icon),
                'method': self.action_relax_fit_relax_time
            })
        if self.relax_disp_flag:
            popup_menus.append({
                'id': wx.NewId(),
                'text': "Set the relaxation &time",
                'icon': fetch_icon(uf_info.get_uf('relax_disp.relax_time').gui_icon),
                'method': self.action_relax_disp_relax_time
            })
            popup_menus.append({
                'id': wx.NewId(),
                'text': "Set the spectrometer &frequency",
                'icon': fetch_icon("relax.spectrometer"),
                'method': self.action_spectrometer_frq
            })
        if self.relax_disp_flag and is_r1rho_exp_type(id):
            popup_menus.append({
                'id': wx.NewId(),
                'text': u("Set the spin-&lock field strength \u03BD1"),
                'icon': fetch_icon("relax.relax_disp"),
                'method': self.action_relax_disp_spin_lock_field
            })
            popup_menus.append({
                'id': wx.NewId(),
                'text': u("Set the spin-&lock offset \u03C9_rf"),
                'icon': fetch_icon("relax.relax_disp"),
                'method': self.action_relax_disp_spin_lock_offset
            })
        if self.relax_disp_flag and is_cpmg_exp_type(id):
            popup_menus.append({
                'id': wx.NewId(),
                'text': u("Set the &CPMG pulse sequence information"),
                'icon': fetch_icon("relax.relax_disp"),
                'method': self.action_relax_disp_cpmg_setup
            })

        # Return the menu.
        return popup_menus


    def noe_spectrum_type(self, index):
        """Add the NOE spectral type info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if a spectrum type exists, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'spectrum_type') or not len(cdp.spectrum_type):
            return False

        # Append a column.
        self.element.InsertColumn(index, str_to_gui("NOE spectrum type"))

        # Translation table.
        table = {
            'sat': 'Saturated',
            'ref': 'Reference'
        }

        # No data.
        if not hasattr(cdp, 'spectrum_ids'):
            return True

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.spectrum_type.keys():
                continue

            # Set the value.
            self.element.SetStringItem(i, index, str_to_gui(table[cdp.spectrum_type[cdp.spectrum_ids[i]]]))

        # Successful.
        return True


    def relax_times(self, index):
        """Add the relaxation delay time info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if relaxation times exist, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'relax_times') or not len(cdp.relax_times):
            return False

        # Append a column.
        self.element.InsertColumn(index, str_to_gui("Delay times (s)"))

        # No data.
        if not hasattr(cdp, 'spectrum_ids'):
            return True

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.relax_times.keys():
                continue

            # Set the value.
            self.element.SetStringItem(i, index, float_to_gui(cdp.relax_times[cdp.spectrum_ids[i]]))

        # Successful.
        return True


    def replicates(self, index):
        """Add the replicated spectra info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if relaxation times exist, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'replicates') or not len(cdp.replicates):
            return False

        # Replicated spectra.
        repl = replicated_flags()

        # Append a column.
        self.element.InsertColumn(index, str_to_gui("Replicate IDs"))

        # No data.
        if not hasattr(cdp, 'spectrum_ids'):
            return True

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No replicates.
            if not repl[cdp.spectrum_ids[i]]:
                continue

            # The replicated spectra.
            id_list = replicated_ids(cdp.spectrum_ids[i])

            # Convert to a string.
            text = ''
            for j in range(len(id_list)):
                # Add the id.
                text = "%s%s" % (text, id_list[j])

                # Separator.
                if j < len(id_list)-1:
                    text = "%s, " % text

            # Set the value.
            self.element.SetStringItem(i, index, str_to_gui(text))

        # Successful.
        return True


    def setup(self):
        """Override the base variables."""

        # GUI variables.
        self.title = "Spectra list"
        self.observer_base_name = "spectra list"

        # The column titles.
        self.columns = []

        # Button set up.
        self.button_placement = 'top'
        self.button_size = (170, 40)
        self.button_info = [
            {
                'object': 'button_add',
                'label': ' Add',
                'icon': fetch_icon('oxygen.actions.list-add-relax-blue', "22x22"),
                'method': self.fn_add,
                'tooltip': "Read a spectral data file."
            }, {
                'object': 'button_delete',
                'label': ' Delete',
                'icon': fetch_icon('oxygen.actions.list-remove', "22x22"),
                'method': self.action_spectrum_delete,
                'tooltip': "Delete loaded relaxation data from the relax data store."
            }, {
                'object': 'button_error_analysis',
                'label': ' Error analysis',
                'icon': fetch_icon('oxygen.categories.applications-education', "22x22"),
                'method': self.action_spectrum_error_analysis,
                'tooltip': "Perform a peak intensity error analysis on the currently loaded data or data subsets.  Select a subset of the spectra below to perform the error analysis only on this subset."
            }
        ]


    def update_data(self):
        """Method called from self.build_element_safe() to update the list data."""

        # Initialise the column index for the data.
        index = 1

        # Delete the rows and columns.
        self.element.DeleteAllItems()
        self.element.DeleteAllColumns()

        # Initialise to a single column.
        self.element.InsertColumn(0, str_to_gui("Spectrum ID"))

        # Expand the number of rows to match the number of spectrum IDs, and add the IDs.
        n = 0
        if hasattr(cdp, 'spectrum_ids'):
            # The number of IDs.
            n = len(cdp.spectrum_ids)

            # Set the IDs.
            for i in range(n):
                self.element.InsertStringItem(i, str_to_gui(cdp.spectrum_ids[i]))

        # The NOE spectrum type.
        if self.noe_spectrum_type(index):
            index += 1

        # The experiment type.
        if self.relax_disp_flag and self.add_exp_type(index):
            index += 1

        # The spectrometer frequency.
        if self.relax_disp_flag and self.add_frqs(index):
            index += 1

        # The spin-lock field strength or CPMG pulse frequency.
        if self.relax_disp_flag and self.add_disp_point(index):
            index += 1

        # The offset.
        if self.relax_disp_flag and self.add_offset(index):
            index += 1

        # The relaxation times.
        if (self.relax_fit_flag or self.relax_disp_flag) and self.relax_times(index):
            index += 1

        # The replicated spectra.
        if self.replicates(index):
            index += 1
