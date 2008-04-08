###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
import sys
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store


class Sequence(TestCase):
    """Class for testing the sequence functions."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_load_protein_N_spins_from_pdb(self):
        """Load the protein backbone amide N spins from a loaded PDB file."""

        # Read the PDB file.
        self.relax.interpreter._Structure.read_pdb(file='test.pdb', dir=sys.path[-1] + '/test_suite/system_tests/data', model=1)

        # Generate the sequence (1 molecule, all residues, and only N spins).
        self.relax.interpreter._Structure.load_spins(spin_id='@N')

        # Alias the current data pipe.
        cdp = relax_data_store[relax_data_store.current_pipe]

        # Test some of the sequence.
        self.assertEqual(len(cdp.mol), 1)
        self.assertEqual(cdp.mol[0].name, None)
        self.assertEqual(len(cdp.mol[0].res), 12)

        # 1st residue.
        self.assertEqual(cdp.mol[0].res[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[0].spin), 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].num, 1)
        self.assertEqual(cdp.mol[0].res[0].spin[0].name, 'N')

        # 2nd residue.
        self.assertEqual(cdp.mol[0].res[1].num, 2)
        self.assertEqual(cdp.mol[0].res[1].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[1].spin), 1)
        self.assertEqual(cdp.mol[0].res[1].spin[0].num, 11)
        self.assertEqual(cdp.mol[0].res[1].spin[0].name, 'N')

        # 3rd residue.
        self.assertEqual(cdp.mol[0].res[2].num, 3)
        self.assertEqual(cdp.mol[0].res[2].name, 'LEU')
        self.assertEqual(len(cdp.mol[0].res[2].spin), 1)
        self.assertEqual(cdp.mol[0].res[2].spin[0].num, 28)
        self.assertEqual(cdp.mol[0].res[2].spin[0].name, 'N')

        # 4th residue.
        self.assertEqual(cdp.mol[0].res[3].num, 4)
        self.assertEqual(cdp.mol[0].res[3].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[3].spin), 1)
        self.assertEqual(cdp.mol[0].res[3].spin[0].num, 51)
        self.assertEqual(cdp.mol[0].res[3].spin[0].name, 'N')

        # 5th residue.
        self.assertEqual(cdp.mol[0].res[4].num, 5)
        self.assertEqual(cdp.mol[0].res[4].name, 'SER')
        self.assertEqual(len(cdp.mol[0].res[4].spin), 1)
        self.assertEqual(cdp.mol[0].res[4].spin[0].num, 59)
        self.assertEqual(cdp.mol[0].res[4].spin[0].name, 'N')

        # 6th residue.
        self.assertEqual(cdp.mol[0].res[5].num, 6)
        self.assertEqual(cdp.mol[0].res[5].name, 'MET')
        self.assertEqual(len(cdp.mol[0].res[5].spin), 1)
        self.assertEqual(cdp.mol[0].res[5].spin[0].num, 71)
        self.assertEqual(cdp.mol[0].res[5].spin[0].name, 'N')

        # 7th residue.
        self.assertEqual(cdp.mol[0].res[6].num, 7)
        self.assertEqual(cdp.mol[0].res[6].name, 'ASP')
        self.assertEqual(len(cdp.mol[0].res[6].spin), 1)
        self.assertEqual(cdp.mol[0].res[6].spin[0].num, 91)
        self.assertEqual(cdp.mol[0].res[6].spin[0].name, 'N')

        # 8th residue.
        self.assertEqual(cdp.mol[0].res[7].num, 8)
        self.assertEqual(cdp.mol[0].res[7].name, 'SER')
        self.assertEqual(len(cdp.mol[0].res[7].spin), 1)
        self.assertEqual(cdp.mol[0].res[7].spin[0].num, 104)
        self.assertEqual(cdp.mol[0].res[7].spin[0].name, 'N')

        # 9th residue.
        self.assertEqual(cdp.mol[0].res[8].num, 9)
        self.assertEqual(cdp.mol[0].res[8].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[8].spin), 1)
        self.assertEqual(cdp.mol[0].res[8].spin[0].num, 116)
        self.assertEqual(cdp.mol[0].res[8].spin[0].name, 'N')

        # 10th residue.
        self.assertEqual(cdp.mol[0].res[9].num, 10)
        self.assertEqual(cdp.mol[0].res[9].name, 'PRO')
        self.assertEqual(len(cdp.mol[0].res[9].spin), 1)
        self.assertEqual(cdp.mol[0].res[9].spin[0].num, 133)
        self.assertEqual(cdp.mol[0].res[9].spin[0].name, 'N')

        # 11th residue.
        self.assertEqual(cdp.mol[0].res[10].num, 11)
        self.assertEqual(cdp.mol[0].res[10].name, 'GLU')
        self.assertEqual(len(cdp.mol[0].res[10].spin), 1)
        self.assertEqual(cdp.mol[0].res[10].spin[0].num, 150)
        self.assertEqual(cdp.mol[0].res[10].spin[0].name, 'N')

        # 12th residue.
        self.assertEqual(cdp.mol[0].res[11].num, 12)
        self.assertEqual(cdp.mol[0].res[11].name, 'GLY')
        self.assertEqual(len(cdp.mol[0].res[11].spin), 1)
        self.assertEqual(cdp.mol[0].res[11].spin[0].num, 167)
        self.assertEqual(cdp.mol[0].res[11].spin[0].name, 'N')


    def test_read(self):
        """The sequence.read() test."""

        # Read the sequence.
        self.relax.interpreter._Sequence.read(file='test_seq', dir=sys.path[-1] + '/test_suite/system_tests/data')
