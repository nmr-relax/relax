###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

# relax module imports.
from data import Data as relax_data_store



class Sequence_base_class:
    """Base class for the tests of both the 'prompt.sequence' and 'generic_fns.sequence' modules.

    This base class also contains many shared unit tests.
    """

    def setUp(self):
        """Set up for all the molecule unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_read_protein_noe_data(self):
        """Test the reading of the amino acid sequence out of a protein NOE data file.

        The functions tested are generic_fns.sequence.read() and prompt.sequence.read().
        """

        # Read the residue sequence out of the Ap4Aase 600 MHz NOE data file.
        self.sequence_fns.read(file='Ap4Aase.Noe.600.bz2', dir='../../shared_data/relaxation_data')

        # Test parts of the sequence.
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'GLY')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 2)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'PRO')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 3)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'LEU')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 4)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'GLY')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 5)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'SER')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 90)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'GLU')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 91)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'LYS')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 92)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'LEU')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 163)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'PRO')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 164)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'ISS')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 165)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'LEU')
