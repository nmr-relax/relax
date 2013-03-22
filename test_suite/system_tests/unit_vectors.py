###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
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
import dep_check
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Unit_vectors(SystemTestCase):
    """Class for testing the calculation of unit vectors."""

    def __init__(self, methodName='runTest'):
        """Skip scientific Python tests if not installed.

        @keyword methodName:    The name of the test.
        @type methodName:       str
        """

        # Execute the base class method.
        super(Unit_vectors, self).__init__(methodName)


    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_calc_unit_vectors1(self):
        """Load the PDB file using the Scientific parser and calculate the XH unit vectors."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='scientific')

        # Load the spins.
        self.interpreter.structure.load_spins(spin_id='@N')
        self.interpreter.structure.load_spins(spin_id='@H')

        # Calculate the unit vectors.
        self.interpreter.dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        self.interpreter.dipole_pair.unit_vectors()

        # Leu 3.
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 24)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assert_(hasattr(cdp.interatomic[0], 'vector'))
        self.assertNotEqual(cdp.interatomic[0].vector, None)
        self.assertAlmostEqual(cdp.interatomic[0].vector[0], 0.40899187)
        self.assertAlmostEqual(cdp.interatomic[0].vector[1], -0.80574458)
        self.assertAlmostEqual(cdp.interatomic[0].vector[2], 0.42837054)


    def test_calc_unit_vectors2(self):
        """Load the PDB file using the Scientific parser and calculate the XH unit vectors (with spin numbers removed)."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='scientific')

        # Load the spins.
        self.interpreter.structure.load_spins(spin_id='@N')
        self.interpreter.structure.load_spins(spin_id='@H')

        # Remove the spin numbers.
        self.interpreter.spin.number(force=True)

        # Calculate the unit vectors.
        self.interpreter.dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        self.interpreter.dipole_pair.unit_vectors()

        # Leu 3.
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assert_(hasattr(cdp.interatomic[0], 'vector'))
        self.assertNotEqual(cdp.interatomic[0].vector, None)
        self.assertAlmostEqual(cdp.interatomic[0].vector[0], 0.40899187)
        self.assertAlmostEqual(cdp.interatomic[0].vector[1], -0.80574458)
        self.assertAlmostEqual(cdp.interatomic[0].vector[2], 0.42837054)


    def test_calc_unit_vectors3(self):
        """Load the PDB file using the internal parser and calculate the XH unit vectors."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Load the spins.
        self.interpreter.structure.load_spins(spin_id='@N')
        self.interpreter.structure.load_spins(spin_id='@H')

        # Calculate the unit vectors.
        self.interpreter.dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        self.interpreter.dipole_pair.unit_vectors()

        # Leu 3.
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 24)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assert_(hasattr(cdp.interatomic[0], 'vector'))
        self.assertNotEqual(cdp.interatomic[0].vector, None)
        self.assertAlmostEqual(cdp.interatomic[0].vector[0], 0.40899187)
        self.assertAlmostEqual(cdp.interatomic[0].vector[1], -0.80574458)
        self.assertAlmostEqual(cdp.interatomic[0].vector[2], 0.42837054)


    def test_calc_unit_vectors4(self):
        """Load the PDB file using the internal parser and calculate the XH unit vectors from it (with spin numbers removed)."""

        # Read the PDB file.
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Load the spins.
        self.interpreter.structure.load_spins(spin_id='@N')
        self.interpreter.structure.load_spins(spin_id='@H')

        # Remove the spin numbers.
        self.interpreter.spin.number(force=True)

        # Calculate the unit vectors.
        self.interpreter.dipole_pair.define(spin_id1='@N', spin_id2='@H', direct_bond=True)
        self.interpreter.dipole_pair.unit_vectors()

        # Leu 3.
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assert_(hasattr(cdp.interatomic[0], 'vector'))
        self.assertNotEqual(cdp.interatomic[0].vector, None)
        self.assertAlmostEqual(cdp.interatomic[0].vector[0], 0.40899187)
        self.assertAlmostEqual(cdp.interatomic[0].vector[1], -0.80574458)
        self.assertAlmostEqual(cdp.interatomic[0].vector[2], 0.42837054)
