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

# Python module imports.
from os import remove, tempnam
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

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

        # Get a temporary file name.
        self.tmpfile = tempnam()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Delete the temporary file.
        try:
            remove(self.tmpfile)
        except OSError:
            pass


    def test_read_protein_noe_data(self):
        """Test the reading of the amino acid sequence out of a protein NOE data file.

        The functions tested are generic_fns.sequence.read() and prompt.sequence.read().
        """

        # Read the residue sequence out of the Ap4Aase 600 MHz NOE data file.
        self.sequence_fns.read(file='Ap4Aase.Noe.600.bz2', dir='../shared_data/relaxation_data')

        # Test parts of the sequence.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'GLY')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'PRO')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].num, 3)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'LEU')
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].name, 'GLY')
        self.assertEqual(relax_data_store['orig'].mol[0].res[4].num, 5)
        self.assertEqual(relax_data_store['orig'].mol[0].res[4].name, 'SER')
        self.assertEqual(relax_data_store['orig'].mol[0].res[80].num, 90)
        self.assertEqual(relax_data_store['orig'].mol[0].res[80].name, 'GLU')
        self.assertEqual(relax_data_store['orig'].mol[0].res[81].num, 91)
        self.assertEqual(relax_data_store['orig'].mol[0].res[81].name, 'LYS')
        self.assertEqual(relax_data_store['orig'].mol[0].res[82].num, 92)
        self.assertEqual(relax_data_store['orig'].mol[0].res[82].name, 'LEU')
        self.assertEqual(relax_data_store['orig'].mol[0].res[151].num, 163)
        self.assertEqual(relax_data_store['orig'].mol[0].res[151].name, 'PRO')
        self.assertEqual(relax_data_store['orig'].mol[0].res[152].num, 164)
        self.assertEqual(relax_data_store['orig'].mol[0].res[152].name, 'HIS')
        self.assertEqual(relax_data_store['orig'].mol[0].res[153].num, 165)
        self.assertEqual(relax_data_store['orig'].mol[0].res[153].name, 'LEU')


    def test_write_protein_sequence(self):
        """Test the writing of an amino acid sequence.

        The functions tested are generic_fns.sequence.write() and prompt.sequence.write().
        """

        # Alias the 'orig' relax data store.
        cdp = relax_data_store['orig']

        # Create a simple animo acid sequence.
        cdp.mol[0].res.add_item('GLY', 1)
        cdp.mol[0].res.add_item('PRO', 2)
        cdp.mol[0].res.add_item('LEU', 3)
        cdp.mol[0].res.add_item('GLY', 4)
        cdp.mol[0].res.add_item('SER', 5)

        # The temporary file.
        tmpfile = tempnam()

        # Write the residue sequence.
        self.sequence_fns.write(file=tmpfile)

        # Open the temp file.
        file = open(tmpfile)

        # Get the md5sum of the file.
        file_md5 = md5()
        file_md5.update(file.read())

        # Test the md5sum.
        self.assertEqual(file_md5, '')
