###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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
from tempfile import mktemp
try:
    from hashlib import md5
except ImportError:
    from md5 import new as md5

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes
from relax_io import delete
from status import Status; status = Status()
from test_suite.unit_tests.base_classes import UnitTestCase


class Sequence_base_class(UnitTestCase):
    """Base class for the tests of both the 'prompt.sequence' and 'generic_fns.sequence' modules.

    This base class also contains many shared unit tests.
    """

    def setUp(self):
        """Set up for all the molecule unit tests."""

        # Add a data pipe to the data store.
        ds.add(pipe_name='orig', pipe_type='mf')

        # Get a temporary file name.
        ds.tmpfile = mktemp()

        # Ap4Aase residue sequence data.
        self.Ap4Aase_res_num = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165]
        self.Ap4Aase_res_name = ['GLY', 'PRO', 'LEU', 'GLY', 'SER', 'MET', 'ASP', 'SER', 'PRO', 'PRO', 'GLU', 'GLY', 'TYR', 'ARG', 'ARG', 'ASN', 'VAL', 'GLY', 'ILE', 'CYS', 'LEU', 'MET', 'ASN', 'ASN', 'ASP', 'LYS', 'LYS', 'ILE', 'PHE', 'ALA', 'ALA', 'SER', 'ARG', 'LEU', 'ASP', 'ILE', 'PRO', 'ASP', 'ALA', 'TRP', 'GLN', 'MET', 'PRO', 'GLN', 'GLY', 'GLY', 'ILE', 'ASP', 'GLU', 'GLY', 'GLU', 'ASP', 'PRO', 'ARG', 'ASN', 'ALA', 'ALA', 'ILE', 'ARG', 'GLU', 'LEU', 'ARG', 'GLU', 'GLU', 'THR', 'GLY', 'VAL', 'THR', 'SER', 'ALA', 'GLU', 'VAL', 'ILE', 'ALA', 'GLU', 'VAL', 'PRO', 'TYR', 'TRP', 'LEU', 'THR', 'TYR', 'ASP', 'PHE', 'PRO', 'PRO', 'LYS', 'VAL', 'ARG', 'GLU', 'LYS', 'LEU', 'ASN', 'ILE', 'GLN', 'TRP', 'GLY', 'SER', 'ASP', 'TRP', 'LYS', 'GLY', 'GLN', 'ALA', 'GLN', 'LYS', 'TRP', 'PHE', 'LEU', 'PHE', 'LYS', 'PHE', 'THR', 'GLY', 'GLN', 'ASP', 'GLN', 'GLU', 'ILE', 'ASN', 'LEU', 'LEU', 'GLY', 'ASP', 'GLY', 'SER', 'GLU', 'LYS', 'PRO', 'GLU', 'PHE', 'GLY', 'GLU', 'TRP', 'SER', 'TRP', 'VAL', 'THR', 'PRO', 'GLU', 'GLN', 'LEU', 'ILE', 'ASP', 'LEU', 'THR', 'VAL', 'GLU', 'PHE', 'LYS', 'LYS', 'PRO', 'VAL', 'TYR', 'LYS', 'GLU', 'VAL', 'LEU', 'SER', 'VAL', 'PHE', 'ALA', 'PRO', 'HIS', 'LEU']


    def test_copy_protein_sequence(self):
        """Test the copying of an amino acid sequence.

        The functions tested are generic_fns.sequence.copy() and prompt.sequence.copy().
        """

        # Get the data pipe.
        dp_orig = pipes.get_pipe('orig')

        # Create a simple animo acid sequence.
        dp_orig.mol[0].res[0].num = 1
        dp_orig.mol[0].res[0].name = 'GLY'
        dp_orig.mol[0].res.add_item('PRO', 2)
        dp_orig.mol[0].res.add_item('LEU', 3)
        dp_orig.mol[0].res.add_item('GLY', 4)
        dp_orig.mol[0].res.add_item('SER', 5)

        # Add an object which should not be copied.
        dp_orig.mol[0].res[2].spin[0].test = True

        # Add a new data pipe to the data store.
        ds.add(pipe_name='new', pipe_type='mf')
        dp_new = pipes.get_pipe('new')

        # Copy the residue sequence.
        self.sequence_fns.copy('orig')

        # Test the sequence.
        self.assertEqual(dp_new.mol[0].res[0].num, 1)
        self.assertEqual(dp_new.mol[0].res[0].name, 'GLY')
        self.assertEqual(dp_new.mol[0].res[1].num, 2)
        self.assertEqual(dp_new.mol[0].res[1].name, 'PRO')
        self.assertEqual(dp_new.mol[0].res[2].num, 3)
        self.assertEqual(dp_new.mol[0].res[2].name, 'LEU')
        self.assertEqual(dp_new.mol[0].res[3].num, 4)
        self.assertEqual(dp_new.mol[0].res[3].name, 'GLY')
        self.assertEqual(dp_new.mol[0].res[4].num, 5)
        self.assertEqual(dp_new.mol[0].res[4].name, 'SER')

        # Test that the extra object was not copied.
        self.assert_(not hasattr(dp_new.mol[0].res[2].spin[0], 'test'))


    def test_display_protein_sequence(self):
        """Test the display of an amino acid sequence.

        The functions tested are generic_fns.sequence.display() and prompt.sequence.display().
        """

        # Get the data pipe.
        dp_orig = pipes.get_pipe('orig')

        # Create a simple animo acid sequence.
        dp_orig.mol[0].res[0].num = 1
        dp_orig.mol[0].res[0].name = 'GLY'
        dp_orig.mol[0].res.add_item('PRO', 2)
        dp_orig.mol[0].res.add_item('LEU', 3)
        dp_orig.mol[0].res.add_item('GLY', 4)
        dp_orig.mol[0].res.add_item('SER', 5)

        # Try displaying the residue sequence.
        self.sequence_fns.display(res_num_flag=True, res_name_flag=True)


    def test_read_protein_noe_data(self):
        """Test the reading of the amino acid sequence out of a protein NOE data file.

        The functions tested are generic_fns.sequence.read() and prompt.sequence.read().
        """

        # Read the residue sequence out of the Ap4Aase 600 MHz NOE data file.
        self.sequence_fns.read(file='Ap4Aase.Noe.600.bz2', dir=status.install_path+sep+'test_suite'+sep+'shared_data'+sep+'relaxation_data', res_num_col=1, res_name_col=2)

        # Get the data pipe.
        dp = pipes.get_pipe('orig')

        # Test the entire sequence.
        for i in xrange(len(self.Ap4Aase_res_num)):
            self.assertEqual(dp.mol[0].res[i].num, self.Ap4Aase_res_num[i])
            self.assertEqual(dp.mol[0].res[i].name, self.Ap4Aase_res_name[i])


    def test_write_protein_sequence(self):
        """Test the writing of an amino acid sequence.

        The functions tested are generic_fns.sequence.write() and prompt.sequence.write().
        """

        # Get the data pipe.
        dp_orig = pipes.get_pipe('orig')

        # Create a simple animo acid sequence.
        dp_orig.mol[0].res[0].num = 1
        dp_orig.mol[0].res[0].name = 'GLY'
        dp_orig.mol[0].res.add_item('PRO', 2)
        dp_orig.mol[0].res.add_item('LEU', 3)
        dp_orig.mol[0].res.add_item('GLY', 4)
        dp_orig.mol[0].res.add_item('SER', 5)

        # Write the residue sequence.
        self.sequence_fns.write(file=ds.tmpfile, res_num_flag=True, res_name_flag=True)

        # Open the temp file.
        file = open(ds.tmpfile)

        # Get the md5sum of the file.
        file_md5 = md5()
        file_md5.update(file.read())

        # Test the md5sum.
        self.assertEqual(file_md5.digest(), '\x98\x7f\xb9\xe0\xb9\x96\x90\x87\x07-\xe3\x87Z\x0b~\xb1')

        # Close the file.
        file.close()
