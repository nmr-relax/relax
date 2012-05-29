###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
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
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Dead_uf_pages(GuiTestCase):
    """Class for testing the failure of user function pages."""

    def test_mol_create(self):
        """Test a failure detected via the molecule.create user function."""

        # The user function objects.
        mol_create = uf_store['molecule.create']
        pipe_create = uf_store['pipe.create']

        # First try to create a molecule (this will fail due to no data pipes being present).
        try:
            # Call the object, then simulate the 'ok' click.
            mol_create(mol_name='x', mol_type='protein')
            mol_create.wizard._ok()
        except RelaxNoPipeError, instance:
            sys.stderr.write(instance.__str__())

        # Create a data pipe.
        pipe_create(pipe_name='test', pipe_type='mf')
        pipe_create.wizard._ok()

        # Try to create the molecule a second time.
        mol_create(mol_name='x', mol_type='protein')
        mol_create.wizard._ok()

        # Checks.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'x')
