###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

"""Module for testing the special features of the user function GUI windows."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.string_conv import float_to_gui, int_to_gui, str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class User_functions(GuiTestCase):
    """Class for testing special features of the user function GUI windows."""

    def test_structure_pdb_read(self):
        """Test the full operation of the structure.read_pdb user function GUI window."""

        # Open the pipe.create user function window, set the args and execute.
        uf = uf_store['pipe.create']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)
        uf.page.SetValue('pipe_name', str_to_gui('PDB reading test'))
        uf.page.SetValue('pipe_type', str_to_gui('mf'))
        uf.wizard._go_next(None)

        # Open the structure.read_pdb user function window.
        uf = uf_store['structure.read_pdb']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)

        # The PDB file to operate on.
        file = status.install_path + sep + 'test_suite' + sep + 'shared_data' + sep + 'structures' + sep + 'trunc_ubi_pcs.pdb'
        uf.page.SetValue('file', str_to_gui(file))

        # Set the models to read.
        uf.page.SetValue('read_model', str_to_gui('6'))
        uf.page.uf_args['read_model'].selection_win_show()
        uf.page.uf_args['read_model'].sel_win.append_row(None)
        uf.page.uf_args['read_model'].sel_win.sequence.SetStringItem(index=0, col=0, label=int_to_gui(2))
        uf.page.uf_args['read_model'].sel_win.sequence.SetStringItem(index=1, col=0, label=int_to_gui(4))
        uf.page.uf_args['read_model'].selection_win_data()

        # Renumber the models.
        uf.page.uf_args['set_model_num'].selection_win_show()
        uf.page.uf_args['set_model_num'].sel_win.append_row(None)
        uf.page.uf_args['set_model_num'].sel_win.append_row(None)
        uf.page.uf_args['set_model_num'].sel_win.sequence.SetStringItem(index=0, col=0, label=int_to_gui(1))
        uf.page.uf_args['set_model_num'].sel_win.sequence.SetStringItem(index=1, col=0, label=int_to_gui(3))
        uf.page.uf_args['set_model_num'].selection_win_data()

        # GUI data checks.
        self.assertEqual(uf.page.uf_args['read_model'].GetValue(), [2, 4])
        self.assertEqual(uf.page.uf_args['set_model_num'].GetValue(), [1, 3])

        # Execute the user function.
        uf.wizard._go_next(None)

        # Check the structural data.
        self.assert_(hasattr(cdp, 'structure'))
        self.assert_(hasattr(cdp.structure, 'structural_data'))
        self.assertEqual(len(cdp.structure.structural_data), 2)
        self.assertEqual(cdp.structure.structural_data[0].num, 1)
        self.assertEqual(cdp.structure.structural_data[1].num, 3)


    def test_value_set(self):
        """Test the full operation of the value.set user function GUI window."""

        # Open the pipe.create user function window, set the args and execute.
        uf = uf_store['pipe.create']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)
        uf.page.SetValue('pipe_name', str_to_gui('value.set user function test'))
        uf.page.SetValue('pipe_type', str_to_gui('mf'))
        uf.wizard._go_next(None)

        # Create a spin to add data to.
        uf = uf_store['spin.create']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)
        uf.page.SetValue('res_num', int_to_gui(1))
        uf.page.SetValue('res_name', str_to_gui('Gly'))
        uf.page.SetValue('spin_name', str_to_gui('N'))
        uf.wizard._go_next(None)

        # Open the value.set user function window.
        uf = uf_store['value.set']
        uf._sync = True
        uf.create_wizard(parent=self.app.gui)
        uf.page.SetValue('val', float_to_gui(-0.000172))
        uf.page.SetValue('param', str_to_gui('csa'))
        uf.wizard._go_next(None)
