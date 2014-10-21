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

# relax module imports.
from pipe_control.pipes import cdp_name
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.string_conv import str_to_gui


class General(GuiTestCase):
    """Class for testing general GUI operations."""

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
