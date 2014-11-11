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
"""Module containing the classes for GUI components involving relaxation data."""

# Python module imports.
import wx

# relax module imports.
from graphics import fetch_icon
from gui.components.base_list import Base_list
from gui.string_conv import gui_to_str, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()
from status import Status; status = Status()
from user_functions.data import Uf_info; uf_info = Uf_info()


class Relax_data_meta_list(Base_list):
    """The GUI element for listing loaded relaxation data."""

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
        uf_store['relax_data.display'](wx_parent=self.parent, ri_id=id)


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
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'peak_intensity_type') and id in cdp.exp_info.peak_intensity_type:
            type = cdp.exp_info.peak_intensity_type[id]

        # Launch the dialog.
        if type == None:
            uf_store['relax_data.peak_intensity_type'](wx_parent=self.parent, ri_id=id)
        else:
            uf_store['relax_data.peak_intensity_type'](wx_parent=self.parent, ri_id=id, type=type)


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
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_calibration') and id in cdp.exp_info.temp_calibrations():
            method = cdp.exp_info.temp_calibration[id]

        # Launch the dialog.
        if method == None:
            uf_store['relax_data.temp_calibration'](wx_parent=self.parent, ri_id=id)
        else:
            uf_store['relax_data.temp_calibration'](wx_parent=self.parent, ri_id=id, method=method)


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
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_control') and id in cdp.exp_info.temp_control:
            method = cdp.exp_info.temp_control[id]

        # Launch the dialog.
        if method == None:
            uf_store['relax_data.temp_control'](wx_parent=self.parent, ri_id=id)
        else:
            uf_store['relax_data.temp_control'](wx_parent=self.parent, ri_id=id, method=method)


    def is_complete(self):
        """Determine if the data input is complete.

        @return:    The answer to the question.
        @rtype:     bool
        """

        # No relaxation data.
        if not hasattr(cdp, 'ri_ids'):
            return True

        # The number of IDs.
        n = len(cdp.ri_ids)

        # Add all the data.
        for i in range(n):
            # The ID.
            id = cdp.ri_ids[i]

            # Check the peak intensity types.
            if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'peak_intensity_type') or not id in cdp.exp_info.peak_intensity_type:
                return False

            # Check the temperature calibration methods.
            if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'temp_calibration') or not id in cdp.exp_info.temp_calibration:
                return False

            # Check the temperature control methods.
            if not hasattr(cdp, 'exp_info') or not hasattr(cdp.exp_info, 'temp_control') or not id in cdp.exp_info.temp_control:
                return False

        # Data input is complete!
        return True


    def set_box_label(self):
        """Set the label of the StaticBox."""

        # Determine if the data input is complete.
        label = self.title
        if self.is_complete():
            label += " (complete)"
        else:
            label += " (incomplete)"

        # Set the label.
        self.data_box.SetLabel(label)


    def setup(self):
        """Override the base variables."""

        # GUI variables.
        self.title = "Relaxation data metadata"
        self.observer_base_name = "relaxation metadata list"
        self.button_placement = None

        # The column titles.
        self.columns = [
            "Relaxation data ID",
            "Peak intensity type",
            "Temperature calibration",
            "Temperature control"
        ]

        # The right click popup menu.
        self.popup_menus = [
            {
                'id': wx.NewId(),
                'text': "Dis&play the relaxation data",
                'icon': fetch_icon(uf_info.get_uf('relax_data.display').gui_icon),
                'method': self.action_relax_data_display
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
            }
        ]


    def update_data(self):
        """Method called from self.build_element_safe() to update the list data."""

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

                # Set the peak intensity types.
                if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'peak_intensity_type') and id in cdp.exp_info.peak_intensity_type:
                    self.element.SetStringItem(i, 1, str_to_gui(cdp.exp_info.peak_intensity_type[id]))

                # Set the temperature calibration methods.
                if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_calibration') and id in cdp.exp_info.temp_calibration:
                    self.element.SetStringItem(i, 2, str_to_gui(cdp.exp_info.temp_calibration[id]))

                # Set the temperature control methods.
                if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'temp_control') and id in cdp.exp_info.temp_control:
                    self.element.SetStringItem(i, 3, str_to_gui(cdp.exp_info.temp_control[id]))
