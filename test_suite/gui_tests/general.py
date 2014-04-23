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
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_noe(None)
        page.analysis_name.SetValue(str_to_gui("NOE test"))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        page.pipe_name.SetValue(str_to_gui('noe'))
        page.pipe_bundle.SetValue(str_to_gui('noe bundle'))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # NOE tab:  Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # NOE tab:  Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle)

        # Mf tab:  Simulate the new analysis wizard.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_mf(None)
        page.analysis_name.SetValue(str_to_gui("Mf test"))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        page.pipe_name.SetValue(str_to_gui('mf'))
        page.pipe_bundle.SetValue(str_to_gui('mf bundle'))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Mf tab:  Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Mf tab:  Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle)

        # NOE tab:  Switch back.
        self.app.gui.analysis.switch_page(index=0)

        # NOE tab:  Closure.
        self.app.gui.analysis.delete_analysis(0)

        # Check that the Mf data pipe is now the current pipe.
        self.assertEqual(cdp_name(), 'mf')
