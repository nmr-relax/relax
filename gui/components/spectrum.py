###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2013 Edward d'Auvergne                                   #
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
from status import Status; status = Status()
from pipe_control.spectrum import replicated_flags, replicated_ids
from graphics import fetch_icon
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui.components.base_list import Base_list
from gui.components.menu import build_menu_item
from gui.fonts import font
from gui.misc import add_border
from gui.string_conv import float_to_gui, gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Spectra_list(Base_list):
    """The GUI element for listing loaded spectral data."""

    def __init__(self, gui=None, parent=None, box=None, id=None, fn_add=None, proportion=0, button_placement='default', relax_times=False, frq_flag=False, spin_lock_flag=False, cpmg_frq_flag=False):
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
        @keyword relax_times:       A flag which if True will activate the relaxation time parts of the GUI element.
        @type relax_times:          bool
        @keyword frq_flag:          A flag which if True will activate the spectrometer frequency parts of the GUI element.
        @type frq_flag:             bool
        @keyword spin_lock_flag:    A flag which if True will activate the spin-lock field strength parts of the GUI element.
        @type spin_lock_flag:       bool
        @keyword cpmg_frq_flag:     A flag which if True will activate the spin-lock field strength parts of the GUI element.
        @type cpmg_frq_flag:        bool
        """

        # Store the arguments.
        self.fn_add = fn_add
        self.relax_times_flag = relax_times
        self.frq_flag = frq_flag
        self.spin_lock_flag = spin_lock_flag
        self.cpmg_frq_flag = cpmg_frq_flag

        # Initialise the base class.
        super(Spectra_list, self).__init__(gui=gui, parent=parent, box=box, id=id, proportion=proportion, button_placement=button_placement)


    def action_frq_set(self, event):
        """Launch the frq.set user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current time.
        frq = None
        if hasattr(cdp, 'spectrometer_frq') and id in cdp.spectrometer_frq:
            frq = cdp.spectrometer_frq[id]

        # Launch the dialog.
        if frq == None:
            uf_store['frq.set'](id=id)
        else:
            uf_store['frq.set'](frq=frq, id=id)


    def action_relax_disp_cpmg_frq(self, event):
        """Launch the relax_disp.cpmg_frq user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current frequency.
        frq = None
        if hasattr(cdp, 'cpmg_frqs') and id in cdp.cpmg_frqs.keys():
            frq = cdp.cpmg_frqs[id]

        # Launch the dialog.
        if time == None:
            uf_store['relax_disp.cpmg_frq'](spectrum_id=id)
        else:
            uf_store['relax_disp.cpmg_frq'](frq=frq, spectrum_id=id)


    def action_relax_disp_spin_lock_field(self, event):
        """Launch the relax_disp.spin_lock_field user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The spin-lock.
        nu1 = None
        if hasattr(cdp, 'spin_lock_nu1') and id in cdp.spin_lock_nu1.keys():
            nu1 = cdp.spin_lock_nu1[id]

        # Launch the dialog.
        if time == None:
            uf_store['relax_disp.spin_lock_field'](spectrum_id=id)
        else:
            uf_store['relax_disp.spin_lock_field'](frq=nu1, spectrum_id=id)


    def action_relax_fit_relax_time(self, event):
        """Launch the relax_fit.relax_time user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
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


    def add_cpmg_frqs(self, index):
        """Add the CPMG pulse frequency info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if the data exists, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'cpmg_frqs') or not len(cdp.cpmg_frqs):
            return False

        # Append a column.
        self.element.InsertColumn(index, u"\u03BDCPMG (Hz)")

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.cpmg_frqs.keys():
                continue

            # Set the value.
            self.element.SetStringItem(i, index, float_to_gui(cdp.cpmg_frqs[cdp.spectrum_ids[i]]))

        # Successful.
        return True


    def add_frqs(self, index):
        """Add the spectrometer frequency info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if the frequency data exists, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'spectrometer_frq') or not len(cdp.spectrometer_frq):
            return False

        # Append a column.
        self.element.InsertColumn(index, u"\u03C9H (MHz)")

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.spectrometer_frq:
                continue

            # Set the value (in MHz).
            self.element.SetStringItem(i, index, float_to_gui(cdp.spectrometer_frq[cdp.spectrum_ids[i]]/1e6))

        # Successful.
        return True


    def add_spin_lock(self, index):
        """Add the spin-lock field strength info to the element.

        @param index:   The column index for the data.
        @type index:    int
        @return:        True if the data exists, False otherwise.
        @rtype:         bool
        """

        # No type info.
        if not hasattr(cdp, 'spin_lock_nu1') or not len(cdp.spin_lock_nu1):
            return False

        # Append a column.
        self.element.InsertColumn(index, u"Spin-lock \u03BD1 (Hz)")

        # Set the values.
        for i in range(len(cdp.spectrum_ids)):
            # No value.
            if cdp.spectrum_ids[i] not in cdp.spin_lock_nu1.keys():
                continue

            # Set the value.
            self.element.SetStringItem(i, index, float_to_gui(cdp.spin_lock_nu1[cdp.spectrum_ids[i]]))

        # Successful.
        return True


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
            }
        ]

        # The right click popup menu.
        self.popup_menus = [
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
        if self.relax_times_flag:
            self.popup_menus.append({
                'id': wx.NewId(),
                'text': "Set the relaxation &time",
                'icon': fetch_icon(uf_info.get_uf('relax_fit.relax_time').gui_icon),
                'method': self.action_relax_fit_relax_time
            })
        if self.frq_flag:
            self.popup_menus.append({
                'id': wx.NewId(),
                'text': "Set the spectrometer &frequency",
                'icon': fetch_icon("relax.frq"),
                'method': self.action_frq_set
            })
        if self.spin_lock_flag:
            self.popup_menus.append({
                'id': wx.NewId(),
                'text': u"Set the spin-&lock field strength \u03BD1",
                'icon': fetch_icon("relax.relax_disp"),
                'method': self.action_relax_disp_spin_lock_field
            })
        if self.cpmg_frq_flag:
            self.popup_menus.append({
                'id': wx.NewId(),
                'text': u"Set the &CPMG pulse frequency \u03BDCPMG",
                'icon': fetch_icon("relax.relax_disp"),
                'method': self.action_relax_disp_cpmg_frq
            })


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

        # The spectrometer frequency.
        if self.frq_flag and self.add_frqs(index):
            index += 1

        # The spin-lock field strength.
        if self.spin_lock_flag and self.add_spin_lock(index):
            index += 1

        # The CPMG pulse frequency.
        if self.cpmg_frq_flag and self.add_cpmg_frqs(index):
            index += 1

        # The relaxation times.
        if self.relax_times_flag and self.relax_times(index):
            index += 1

        # The replicated spectra.
        if self.replicates(index):
            index += 1
