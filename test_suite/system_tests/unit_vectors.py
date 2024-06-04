###############################################################################
#                                                                             #
# Copyright (C) 2008,2010-2012 Edward d'Auvergne                              #
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


class Unit_vectors(SystemTestCase):
    """Class for testing the calculation of unit vectors."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_calc_unit_vectors1(self):
        """Load the PDB file and calculate the XH unit vectors."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Load the spins.
        self.interpreter.structure.load_spins(spin_id='@N')
        self.interpreter.structure.load_spins(spin_id='@H')

        # Calculate the unit vectors.
        self.interpreter.interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        self.interpreter.interatom.unit_vectors()

        # Leu 3.
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 24)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertTrue(hasattr(cdp.interatomic[0], 'vector'))
        self.assertTrue(cdp.interatomic[0].vector is not None)
        self.assertAlmostEqual(cdp.interatomic[0].vector[0], 0.40899187)
        self.assertAlmostEqual(cdp.interatomic[0].vector[1], -0.80574458)
        self.assertAlmostEqual(cdp.interatomic[0].vector[2], 0.42837054)


    def test_calc_unit_vectors2(self):
        """Load the PDB file and calculate the XH unit vectors (with spin numbers removed)."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)

        # Load the spins.
        self.interpreter.structure.load_spins(spin_id='@N')
        self.interpreter.structure.load_spins(spin_id='@H')

        # Remove the spin numbers.
        self.interpreter.spin.number(force=True)

        # Calculate the unit vectors.
        self.interpreter.interatom.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        self.interpreter.interatom.unit_vectors()

        # Leu 3.
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertTrue(hasattr(cdp.interatomic[0], 'vector'))
        self.assertTrue(cdp.interatomic[0].vector is not None)
        self.assertAlmostEqual(cdp.interatomic[0].vector[0], 0.40899187)
        self.assertAlmostEqual(cdp.interatomic[0].vector[1], -0.80574458)
        self.assertAlmostEqual(cdp.interatomic[0].vector[2], 0.42837054)
