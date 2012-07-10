###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################

# Module docstring.
"""GUI tests for catching dead user function pages."""

# Python module imports.
import sys

# relax module imports.
from relax_errors import RelaxNoPipeError
from test_suite.gui_tests.base_classes import GuiTestCase

# relax GUI imports.
from gui.interpreter import Interpreter; interpreter = Interpreter()
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Dead_uf_pages(GuiTestCase):
    """Class for testing the failure of user function pages."""

    def test_mol_create(self):
        """Test a failure detected via the molecule.create user function."""

        # First try to create a molecule (this will fail due to no data pipes being present).
        try:
            # Call the object.
            self._execute_uf(uf_name='molecule.create', mol_name='x', mol_type='protein')
        except RelaxNoPipeError, instance:
            sys.stderr.write(instance.__str__())

        # Create a data pipe.
        self._execute_uf(uf_name='pipe.create', pipe_name='test', pipe_type='mf')

        # Try to create the molecule a second time.
        self._execute_uf(uf_name='molecule.create', mol_name='x', mol_type='protein')

        # Checks.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'x')
