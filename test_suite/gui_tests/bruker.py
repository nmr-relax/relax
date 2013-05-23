###############################################################################
#                                                                             #
# Copyright (C) 2012-2013 Edward d'Auvergne                                   #
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
"""GUI tests for the Bruker Dynamics Center support."""

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
import dep_check
from pipe_control.mol_res_spin import spin_loop
from lib.errors import RelaxError
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase
from test_suite import system_tests

# relax GUI imports.
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import str_to_gui


class Bruker(GuiTestCase, system_tests.bruker.Bruker):
    """Class for testing the Bruker Dynamics Center support in the GUI."""

    def __init__(self, methodName=None):
        """Set up the test case class for the system tests."""

        # Force execution of the GuiTestCase __init__ method.
        GuiTestCase.__init__(self, methodName)


    def setUp(self):
        """Set up for all the GUI tests."""

        # Run the GuiTestCase setup.
        GuiTestCase.setUp(self)

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_bug_20152_read_dc_file(self):
        """Test the reading of a DC file, catching U{bug #20152<https://gna.org/bugs/?20152>}."""

        # Simulate the new analysis wizard.
        self.app.gui.analysis.menu_new(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(0)
        page.select_mf(None)
        page.analysis_name.SetValue(str_to_gui("Model-free test"))
        self.app.gui.analysis.new_wizard.wizard._go_next(None)
        page = self.app.gui.analysis.new_wizard.wizard.get_page(1)
        self.app.gui.analysis.new_wizard.wizard._go_next(None)

        # Get the data.
        analysis_type, analysis_name, pipe_name, pipe_bundle, uf_exec = self.app.gui.analysis.new_wizard.get_data()

        # Set up the analysis.
        self.app.gui.analysis.new_analysis(analysis_type=analysis_type, analysis_name=analysis_name, pipe_name=pipe_name, pipe_bundle=pipe_bundle)

        # Alias the analysis.
        analysis = self.app.gui.analysis.get_page_from_name("Model-free test")

        # Change the results directory.
        analysis.field_results_dir.SetValue(str_to_gui(ds.tmpdir))

        # Launch the spin viewer window.
        self.app.gui.show_tree()

        # Spin loading wizard:  Initialisation.
        self.app.gui.spin_viewer.load_spins_wizard()

        # Spin loading wizard:  The PDB file.
        page = self.app.gui.spin_viewer.wizard.get_page(0)
        page.selection = 'new pdb'
        self.app.gui.spin_viewer.wizard._go_next()
        page = self.app.gui.spin_viewer.wizard.get_page(self.app.gui.spin_viewer.wizard._current_page)
        page.uf_args['file'].SetValue(str_to_gui(status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'structures' + sep + '1UBQ_H_trunc.pdb'))
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Spin loading wizard:  The spin loading.
        self.app.gui.spin_viewer.wizard._go_next()
        interpreter.flush()    # Required because of the asynchronous uf call.

        # Close the spin viewer window.
        self.app.gui.spin_viewer.handler_close()

        # Flush the interpreter in preparation for the synchronous user functions of the peak list wizard.
        interpreter.flush()

        # The data path.
        data_path = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'model_free' + sep + 'sphere' + sep

        # Set up the Bruker DC wizard.
        analysis.relax_data.wizard_bruker(None)

        # The spectrum.
        page = analysis.relax_data.wizard.get_page(analysis.relax_data.page_indices['read'])
        page.uf_args['ri_id'].SetValue(str_to_gui('r1_700'))
        page.uf_args['file'].SetValue(str_to_gui(status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'bruker_files' + sep + 'T1_demo_1UBQ_H_trunc.txt'))

        # Cause the failure.
        analysis.relax_data.wizard._go_next(None)

        # Check that no data was loaded.
        self.assert_(not hasattr(cdp, 'ri_ids'))
        self.assert_(not hasattr(cdp, 'spectrometer_frq'))
        self.assert_(not hasattr(cdp, 'ri_type'))
        for spin in spin_loop():
            self.assert_(not hasattr(spin, 'ri_data'))
            self.assert_(not hasattr(spin, 'ri_data_err'))
