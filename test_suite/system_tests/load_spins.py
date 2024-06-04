###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Load_spins(SystemTestCase):
    """TestCase class for the loading of spins into the molecule/residue/spin data structure."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_load_spins_from_small_molecule(self):
        """Test the loading of spins from a small molecule."""

        # Execute a relax script.
        self.script_exec(status.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'load_spins_from_small_molecule.py')

        # Test the molecule and residue data.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, 'gromacs_mol1')
        self.assertEqual(len(cdp.mol[0].res), 1)
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'PYR')

        # Spin info.
        nums = [4, 6, 8, 10, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 15, 16, 28, 30]
        names = ['H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10', 'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20', 'H21', 'H22', 'H23', 'H24', 'H25', 'H26', 'H27', 'H28', 'C5', 'C6', 'C19', 'C23']
        elements = ['H']*28 + ['C']*4

        # Loop over the spin containers, testing each.
        self.assertEqual(len(cdp.mol[0].res[0].spin), 32)
        for i in range(len(cdp.mol[0].res[0].spin)):
            self.assertEqual(cdp.mol[0].res[0].spin[i].num, nums[i])
            self.assertEqual(cdp.mol[0].res[0].spin[i].name, names[i])
            self.assertEqual(cdp.mol[0].res[0].spin[i].element, elements[i])
            self.assertTrue(hasattr(cdp.mol[0].res[0].spin[i], 'pos'))
