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
"""Module containing the classes for GUI components involving relaxation data."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from graphics import fetch_icon
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()

# relax GUI module imports.
from gui.components.base_list import Base_list
from gui.components.menu import build_menu_item
from gui.components.relax_data_meta import Relax_data_meta_list
from gui.fonts import font
from gui.icons import relax_icons
from gui.misc import add_border
from gui.string_conv import float_to_gui, gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from gui.wizards.wiz_objects import Wiz_window


class Relax_data_list(Base_list):
    """The GUI element for listing loaded relaxation data."""

    def action_relax_data_delete(self, event):
        """Launch the relax_data.delete user function.

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
        uf_store['relax_data.delete'](ri_id=id)


    def action_relax_data_display(self, event):
        """Launch the relax_data.display user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # Launch the dialog.
        uf_store['relax_data.display'](ri_id=id)


    def action_relax_data_peak_intensity_type(self, event):
        """Launch the relax_data.peak_intensity_type user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current type.
        type = None
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'peak_intensity_type') and id in cdp.exp_info.peak_intensity_type.keys():
            type = cdp.exp_info.peak_intensity_type[id]

        # Launch the dialog.
        if type == None:
            uf_store['relax_data.peak_intensity_type'](ri_id=id)
        else:
            uf_store['relax_data.peak_intensity_type'](ri_id=id, type=type)


    def action_relax_data_temp_calibration(self, event):
        """Launch the relax_data.temp_calibration user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current method.
        method = None
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_calibration') and id in cdp.exp_info.temp_calibration.keys():
            method = cdp.exp_info.temp_calibration[id]

        # Launch the dialog.
        if method == None:
            uf_store['relax_data.temp_calibration'](ri_id=id)
        else:
            uf_store['relax_data.temp_calibration'](ri_id=id, method=method)


    def action_relax_data_temp_control(self, event):
        """Launch the relax_data.temp_control user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current method.
        method = None
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_control') and id in cdp.exp_info.temp_control.keys():
            method = cdp.exp_info.temp_control[id]

        # Launch the dialog.
        if method == None:
            uf_store['relax_data.temp_control'](ri_id=id)
        else:
            uf_store['relax_data.temp_control'](ri_id=id, method=method)


    def action_relax_data_type(self, event):
        """Launch the relax_data.type user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current type.
        type = None
        if hasattr(cdp, 'ri_type') and id in cdp.ri_type.keys():
            type = cdp.ri_type[id]

        # Launch the dialog.
        if type == None:
            uf_store['relax_data.type'](ri_id=id)
        else:
            uf_store['relax_data.type'](ri_id=id, ri_type=type)


    def action_spectrometer_frequency(self, event):
        """Launch the spectrometer.frequency user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The current selection.
        item = self.element.GetFirstSelected()

        # The spectrum ID.
        id = gui_to_str(self.element.GetItemText(item))

        # The current frequency.
        frq = None
        if hasattr(cdp, 'spectrometer_frq') and id in cdp.spectrometer_frq.keys():
            frq = cdp.spectrometer_frq[id]

        # Launch the dialog.
        if frq == None:
            uf_store['spectrometer.frequency'](id=id)
        else:
            uf_store['spectrometer.frequency'](id=id, frq=frq)


    def setup(self):
        """Override the base variables."""

        # GUI variables.
        self.title = "Relaxation data list"
        self.observer_base_name = "relaxation data list"

        # The column titles.
        self.columns = [
            "Relaxation data ID",
            "Data type",
            "Frequency (Hz)"
        ]

        # Button set up.
        self.button_placement = 'top'
        self.button_size = (170, 40)
        self.button_info = [
            {
                'object': 'button_add',
                'label': ' Add',
                'icon': fetch_icon('oxygen.actions.list-add-relax-blue', "22x22"),
                'method': self.wizard_relax_data,
                'tooltip': "Read relaxation data from a file."
            }, {
                'object': 'button_bruker',
                'label': ' Add',
                'icon': fetch_icon('relax.bruker_add', "22x22"),
                'method': self.wizard_bruker,
                'tooltip': "Read a Bruker Dynamics Center relaxation data file."
            }, {
                'object': 'button_delete',
                'label': ' Delete',
                'icon': fetch_icon('oxygen.actions.list-remove', "22x22"),
                'method': self.action_relax_data_delete,
                'tooltip': "Delete loaded relaxation data from the relax data store."
            }, {
                'object': 'button_metadata',
                'label': ' View metadata',
                'icon': fetch_icon('oxygen.mimetypes.text-x-texinfo', "22x22"),
                'method': self.view_metadata,
                'tooltip': "View and edit the relaxation data metadata."
            }
        ]

        # The right click popup menu.
        self.popup_menus = [
            {
                'id': wx.NewId(),
                'text': "&Delete the relaxation data",
                'icon': fetch_icon(uf_info.get_uf('relax_data.delete').gui_icon),
                'method': self.action_relax_data_delete
            }, {
                'id': wx.NewId(),
                'text': "Dis&play the relaxation data",
                'icon': fetch_icon(uf_info.get_uf('relax_data.display').gui_icon),
                'method': self.action_relax_data_display
            }, {
                'id': wx.NewId(),
                'text': "Set the relaxation data &frequency",
                'icon': fetch_icon(uf_info.get_uf('spectrometer.frequency').gui_icon),
                'method': self.action_spectrometer_frequency
            }, {
                'id': wx.NewId(),
                'text': "Set the peak &intensity type",
                'icon': fetch_icon(uf_info.get_uf('relax_data.peak_intensity_type').gui_icon),
                'method': self.action_relax_data_peak_intensity_type
            }, {
                'id': wx.NewId(),
                'text': "Set the temperature &calibration",
                'icon': fetch_icon(uf_info.get_uf('relax_data.temp_calibration').gui_icon),
                'method': self.action_relax_data_temp_calibration
            }, {
                'id': wx.NewId(),
                'text': "Set the temperature c&ontrol",
                'icon': fetch_icon(uf_info.get_uf('relax_data.temp_control').gui_icon),
                'method': self.action_relax_data_temp_control
            }, {
                'id': wx.NewId(),
                'text': "Set the relaxation data &type",
                'icon': fetch_icon(uf_info.get_uf('relax_data.type').gui_icon),
                'method': self.action_relax_data_type
            }
        ]


    def update_data(self):
        """Method called from self.build_element_safe() to update the list data."""

        # Translation table for the Rx data types.
        table = {
            "NOE": "Steady-state NOE",
            "R1": u"R\u2081 longitudinal relaxation",
            "R2": u"R\u2082 transverse relaxation"
        }

        # Expand the number of rows to match the number of relaxation IDs, and add the IDs.
        n = 0
        if hasattr(cdp, 'ri_ids'):
            # The number of IDs.
            n = len(cdp.ri_ids)

            # Add all the data.
            for i in range(n):
                # Set the IDs.
                id = cdp.ri_ids[i]
                self.element.InsertStringItem(i, str_to_gui(id))

                # Set the data types.
                self.element.SetStringItem(i, 1, str_to_gui(table[cdp.ri_type[id]]))

                # Set the frequencies.
                self.element.SetStringItem(i, 2, float_to_gui(cdp.spectrometer_frq[id]))


    def view_metadata(self, event=None):
        """Launch the metadata window.

        @keyword event: The wx event.
        @type event:    wx event
        """

        # Launch.
        Metadata_window(self.gui)


    def wizard_bruker(self, event):
        """Launch the Bruker Dynamics Centre data reading wizard.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The wizard.
        self.wizard_exec(bruker=True)


    def wizard_exec(self, bruker=False):
        """Launch the Rx peak loading wizard.

        @keyword bruker:    A flag which if True will launch the Bruker Dynamics Centre data reading wizard and if False will launch the relaxation data reading wizard
        @type bruker:       bool
        """

        # Change the cursor to busy.
        wx.BeginBusyCursor()

        # The title.
        if bruker:
            title = "The Bruker Dynamics Centre data reading wizard"
        else:
            title = "The relaxation data reading wizard"

        # Initialise a wizard.
        self.wizard = Wiz_window(parent=self.gui, size_x=1000, size_y=800, title=title)
        self.page_indices = {}

        # The reading page.
        if bruker:
            page = uf_store['bruker.read'].create_page(self.wizard, sync=True)
        else:
            page = uf_store['relax_data.read'].create_page(self.wizard, sync=True)
        self.page_indices['read'] = self.wizard.add_page(page, skip_button=True, proceed_on_error=False)

        # The peak intensity type page.
        page = uf_store['relax_data.peak_intensity_type'].create_page(self.wizard, sync=True)
        self.page_indices['peak_intensity_type'] = self.wizard.add_page(page, apply_button=True, skip_button=True)
        page.on_display_post = self.wizard_update_int_type

        # The temperature calibration page.
        page = uf_store['relax_data.temp_calibration'].create_page(self.wizard, sync=True)
        self.page_indices['temp_calibration'] = self.wizard.add_page(page, apply_button=True, skip_button=True)
        page.on_display_post = self.wizard_update_temp_calibration

        # The temperature control page.
        page = uf_store['relax_data.temp_control'].create_page(self.wizard, sync=True)
        self.page_indices['temp_control'] = self.wizard.add_page(page, apply_button=True)
        page.on_display_post = self.wizard_update_temp_control

        # Reset the cursor.
        if wx.IsBusy():
            wx.EndBusyCursor()

        # Run the wizard.
        self.wizard.run()


    def wizard_relax_data(self, event):
        """Launch the relaxation data reading wizard.

        @param event:   The wx event.
        @type event:    wx event
        """

        # The wizard.
        self.wizard_exec(bruker=False)


    def wizard_update_int_type(self):
        """Update the relax_data.peak_intensity_type page based on previous data."""

        # The relax_data.peak_intensity_type page.
        page = self.wizard.get_page(self.page_indices['read'])

        # Get the Rx ID.
        id = page.uf_args['ri_id'].GetValue()

        # Set the ID in the relax_data.peak_intensity_type page.
        page = self.wizard.get_page(self.page_indices['peak_intensity_type'])
        page.uf_args['ri_id'].SetValue(value=id)


    def wizard_update_temp_calibration(self):
        """Update the relax_data.temp_calibration page based on previous data."""

        # The relax_data.temp_calibration page.
        page = self.wizard.get_page(self.page_indices['read'])

        # Get the Rx ID.
        id = page.uf_args['ri_id'].GetValue()

        # Set the ID in the relax_data.temp_calibration page.
        page = self.wizard.get_page(self.page_indices['temp_calibration'])
        page.uf_args['ri_id'].SetValue(value=id)


    def wizard_update_temp_control(self):
        """Update the relax_data.temp_control page based on previous data."""

        # The relax_data.temp_control page.
        page = self.wizard.get_page(self.page_indices['read'])

        # Get the Rx ID.
        id = page.uf_args['ri_id'].GetValue()

        # Set the ID in the relax_data.temp_control page.
        page = self.wizard.get_page(self.page_indices['temp_control'])
        page.uf_args['ri_id'].SetValue(value=id)



class Metadata_window(wx.Frame):
    """The relaxation data metadata window."""

    def __init__(self, parent):
        """Set up the export window.

        @param parent:  The parent object.
        @type parent:   wx.Frame instance
        """

        # The window style.
        style = wx.DEFAULT_FRAME_STYLE

        # Initialise the base class, setting the main GUI window as the parent.
        super(Metadata_window, self).__init__(parent, -1, style=style)

        # Some default values.
        self.size_x = 1200
        self.size_y = 500
        self.border = 5
        self.spacer = 10

        # Set up the frame.
        sizer = self.setup_frame()

        # Add the relaxation data metadata list GUI element, with spacing.
        sizer.AddSpacer(15)
        self.relax_data = Relax_data_meta_list(parent=self.main_panel, box=sizer, id='BMRB export', proportion=1)

        # Open the window.
        if status.show_gui:
            self.Show()


    def handler_close(self, event):
        """Event handler for the close window action.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Unregister the observers.
        self.relax_data.observer_register(remove=True)

        # Close the window.
        event.Skip()


    def setup_frame(self):
        """Set up the relax controller frame.
        @return:    The sizer object.
        @rtype:     wx.Sizer instance
        """

        # Set the frame title.
        self.SetTitle("Relaxation data metadata")

        # Set up the window icon.
        self.SetIcons(relax_icons)

        # Place all elements within a panel (to remove the dark grey in MS Windows).
        self.main_panel = wx.Panel(self, -1)

        # Use a grid sizer for packing the main elements.
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_panel.SetSizer(main_sizer)

        # Build the central sizer, with borders.
        sizer = add_border(main_sizer, border=self.border, packing=wx.VERTICAL)

        # Close the window cleanly (unregistering observers).
        self.Bind(wx.EVT_CLOSE, self.handler_close)

        # Set the default size of the controller.
        self.SetSize((self.size_x, self.size_y))

        # Centre the frame.
        self.Centre()

        # Return the central sizer.
        return sizer
