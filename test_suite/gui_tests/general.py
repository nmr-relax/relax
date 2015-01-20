###############################################################################
#                                                                             #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
"""Generic GUI tests."""

# Python module imports.
import wx

# relax module imports.
from pipe_control.pipes import cdp_name
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.string_conv import str_to_gui


class General(GuiTestCase):
    """Class for testing general GUI operations."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Execute the base __init__ methods.
        super(General, self).__init__(methodName)

        # Tests to skip.
        blacklist = [
            'test_new_analysis_wizard_memory_leak'
        ]

        # Skip the blacklisted tests.
        if methodName in blacklist:
            status.skipped_tests.append([methodName, None, self._skip_type])


    def test_bug_21720_pipe_switching_with_tab_closure(self):
        """Catch U{bug #20479<https://gna.org/bugs/?20479>}, the failure to switch pipes when closing non-last tabs."""

        # NOE tab:  Simulate the new analysis wizard.
        analysis = self.new_analysis_wizard(analysis_type='noe', analysis_name='NOE test', pipe_name='noe', pipe_bundle='noe bundle')

        # Mf tab:  Simulate the new analysis wizard.
        analysis = self.new_analysis_wizard(analysis_type='mf', analysis_name='Mf test', pipe_name='mf', pipe_bundle='mf bundle')

        # NOE tab:  Switch back.
        self.app.gui.analysis.switch_page(index=0)

        # NOE tab:  Closure.
        self.app.gui.analysis.delete_analysis(0)

        # Check that the Mf data pipe is now the current pipe.
        self.assertEqual(cdp_name(), 'mf')


    def test_bug_23187_residue_delete_gui(self):
        """Catch U{bug #23187<https://gna.org/bugs/?23187>}, deleting residue in GUI, and then open spin viewer crashes relax."""

        # Mf tab:  Simulate the new analysis wizard.
        analysis = self.new_analysis_wizard(analysis_type='mf', analysis_name='Mf test', pipe_name='mf', pipe_bundle='mf bundle')

        self._execute_uf(uf_name='residue.create', res_num=1)
        self._execute_uf(uf_name='residue.create', res_num=2)

        # Launch the spin viewer window.
        self.app.gui.show_tree()

        # Close the spin viewer window.
        self.app.gui.spin_viewer.handler_close()

        # Delete spin,
        self._execute_uf(uf_name='residue.delete', res_id=":2")

        # Launch the spin viewer window.
        self.app.gui.show_tree()


    def test_new_analysis_wizard_memory_leak(self):
        """Test for memory leaks in the new analysis wizard."""

        # A large loop (to try to reach the USER Object limit in MS Windows).
        for i in range(100):
            # Printout for debugging.
            print("Analysis wizard number %i." % (i+1))

            # Simulate the menu selection, but don't destroy the GUI element.
            self.app.gui.analysis.menu_new(None, destroy=False)

            # Wizard cleanup.
            wx.Yield()
            self.app.gui.analysis.new_wizard.Destroy()
            del self.app.gui.analysis.new_wizard
