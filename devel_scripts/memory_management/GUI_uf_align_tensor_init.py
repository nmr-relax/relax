###############################################################################
#                                                                             #
# Copyright (C) 2015-2016 Edward d'Auvergne                                   #
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

"""Memory test of the time GUI user function."""

# Python module imports.
import wx

# relax module imports.
from gui.string_conv import float_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


# Base module imports.
from GUI_base import Testing_frame


class Frame(Testing_frame):
    """Testing frame."""

    def test(self):
        """Run the test."""

        # Get the App.
        app = wx.GetApp()

        # Repetitive calling of the align_tensor.init user function.
        for i in self.muppy_loop():
            # First reset relax.
            self._execute_uf(uf_name='reset')

            # Set up a data pipe.
            self._execute_uf(uf_name='pipe.create', pipe_name='GUI uf test', pipe_type='N-state')

            # Open the align_tensor.init user function window.
            uf = uf_store['align_tensor.init']
            uf._sync = True
            uf.create_wizard(parent=app.gui)

            # Set the parameters.
            uf.page.uf_args['params'].SetValue(str_to_gui('(0.00000, -0.00017, 0.00016, 0.00060, -0.00019)'))
            uf.page.uf_args['params'].selection_win_show()
            uf.page.uf_args['params'].sel_win.sequence.SetStringItem(0, 1, float_to_gui(0.00037))
            uf.page.uf_args['params'].selection_win_data()

            # Set up the other tensor data.
            uf.page.uf_args['tensor'].SetValue(str_to_gui('Dy'))
            uf.page.uf_args['align_id'].SetValue(str_to_gui('Dy'))

            # Execute.
            uf.wizard._go_next(None)

            # Destroy the user function object.
            uf.Destroy()


# Set up and execute the GUI.
app = wx.App(False)
frame = Frame(None, "GUI memory test")
frame.Show(True)
app.MainLoop()
