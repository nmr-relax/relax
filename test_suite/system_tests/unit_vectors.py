###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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

# Python module imports.
from os import sep
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes


class Unit_vectors(TestCase):
    """Class for testing the calculation of unit vectors."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_calc_unit_vectors1(self):
        """Load the PDB file using the Scientific parser and calculate the XH unit vectors."""

        # Read the PDB file.
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='scientific')

        # Load the spins.
        self.relax.interpreter._Structure.load_spins(spin_id='@N')

        # Calculate the unit vectors.
        self.relax.interpreter._Structure.vectors(attached='H')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Leu 3.
        self.assert_(hasattr(cdp.mol[0].res[2].spin[0], 'xh_vect'))
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 28)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertNotEqual(cdp.mol[0].res[2].spin[0].xh_vect, None)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[0], 0.40899187)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[1], -0.80574458)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[2], 0.42837054)


    def test_calc_unit_vectors2(self):
        """Load the PDB file using the Scientific parser and calculate the XH unit vectors (with spin numbers removed)."""

        # Read the PDB file.
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='scientific')

        # Load the spins.
        self.relax.interpreter._Structure.load_spins(spin_id='@N')

        # Remove the spin numbers.
        self.relax.interpreter._Spin.number(force=True)

        # Calculate the unit vectors.
        self.relax.interpreter._Structure.vectors(attached='H')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Leu 3.
        self.assert_(hasattr(cdp.mol[0].res[2].spin[0], 'xh_vect'))
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertNotEqual(cdp.mol[0].res[2].spin[0].xh_vect, None)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[0], 0.40899187)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[1], -0.80574458)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[2], 0.42837054)


    def test_calc_unit_vectors3(self):
        """Load the PDB file using the internal parser and calculate the XH unit vectors."""

        # Read the PDB file.
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Load the spins.
        self.relax.interpreter._Structure.load_spins(spin_id='@N')

        # Calculate the unit vectors.
        self.relax.interpreter._Structure.vectors(attached='H')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Leu 3.
        self.assert_(hasattr(cdp.mol[0].res[2].spin[0], 'xh_vect'))
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 28)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertNotEqual(cdp.mol[0].res[2].spin[0].xh_vect, None)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[0], 0.40899187)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[1], -0.80574458)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[2], 0.42837054)


    def test_calc_unit_vectors4(self):
        """Load the PDB file using the internal parser and calculate the XH unit vectors from it (with spin numbers removed)."""

        # Read the PDB file.
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Load the spins.
        self.relax.interpreter._Structure.load_spins(spin_id='@N')

        # Remove the spin numbers.
        self.relax.interpreter._Spin.number(force=True)

        # Calculate the unit vectors.
        self.relax.interpreter._Structure.vectors(attached='H')

        # Alias the current data pipe.
        cdp = pipes.get_pipe()

        # Leu 3.
        self.assert_(hasattr(cdp.mol[0].res[2].spin[0], 'xh_vect'))
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, None)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')
        self.assertNotEqual(cdp.mol[0].res[2].spin[0].xh_vect, None)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[0], 0.40899187)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[1], -0.80574458)
        self.assertAlmostEqual(cdp.mol[0].res[2].spin[0].xh_vect[2], 0.42837054)
