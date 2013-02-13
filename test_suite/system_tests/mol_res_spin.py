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
"""System tests of the molecule, residue, and spin sequence operators."""


# Python module imports.
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Mol_res_spin(SystemTestCase):
    """Class for testing the mol_res_spin functions."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_prune_metadata(self):
        """Check the proper pruning of the spin ID metadata."""

        # Create a data pipe for all the data.
        self.interpreter.pipe.create('CaM N-dom', 'N-state')

        # Create some spins.
        self.interpreter.spin.create(spin_name='N', spin_num=1, res_name='Gly', res_num=3, mol_name='CaM')
        self.interpreter.spin.create(spin_name='H', spin_num=2, res_name='Gly', res_num=3, mol_name='CaM')

        # Make sure that certain spin IDs have been removed.
        print("The spin ID lookup table:\n%s" % cdp.mol._spin_id_lookup)
        self.assert_(':3' not in cdp.mol._spin_id_lookup)
        self.assert_('#CaM' not in cdp.mol._spin_id_lookup)

        # Create some more spins.
        self.interpreter.spin.create(spin_name='N', spin_num=3, res_name='Gly', res_num=4, mol_name='CaM')
        self.interpreter.spin.create(spin_name='H', spin_num=4, res_name='Gly', res_num=4, mol_name='CaM')

        # Make sure that certain spin IDs have been removed.
        print("The spin ID lookup table:\n%s" % cdp.mol._spin_id_lookup)
        self.assert_('@N' not in cdp.mol._spin_id_lookup)
        self.assert_('@H' not in cdp.mol._spin_id_lookup)


    def test_residue_delete(self):
        """Test residue deletion."""

        # Read a PDB file.
        self.interpreter.structure.read_pdb(file='sphere.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'sphere')

        # Load the spins.
        self.interpreter.structure.load_spins()

        # Test the original sequence data.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(len(cdp.mol[0].res), 9)

        # Delete the first residue.
        self.interpreter.residue.delete(res_id='#sphere_mol1:1')

        # Test the remaining sequence data.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(len(cdp.mol[0].res), 8)
