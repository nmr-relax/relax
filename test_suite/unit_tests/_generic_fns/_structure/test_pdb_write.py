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

# relax module imports.
from generic_fns.structure import pdb_write
from relax_io import DummyFileObject
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_pdb_write(UnitTestCase):
    """Unit tests for the functions of the 'generic_fns.structure.pdb_write' module."""

    def test_atom(self):
        """Test the generic_fns.structure.pdb_write.atom() function."""

        # A dummy file to write to.
        file = DummyFileObject()

        # Create the PDB record.
        pdb_write.atom(file, serial=158, name='CG', res_name='GLU', res_seq='11', x=9.59, y=-1.041, z=-11.596, occupancy=1.0, temp_factor=0.0, element='C')

        # Test the record.
        records = file.readlines()
        actual = 'ATOM    158 CG   GLU    11       9.590  -1.041 -11.596  1.00  0.00           C  \n'
        print(repr(records[0]))
        print(repr(actual))
        self.assertEqual(records[0], actual)


    def test_helix(self):
        """Test the generic_fns.structure.pdb_write.helix() function."""

        # A dummy file to write to.
        file = DummyFileObject()

        # Create the PDB record.
        pdb_write.helix(file, ser_num=1, helix_id='H1', init_res_name='ILE', init_chain_id='A', init_seq_id=23, init_icode=None, end_res_name='GLU', end_chain_id='A', end_seq_num=34, end_icode=None, helix_class=1, comment=None, length=12)

        # Test the record.
        records = file.readlines()
        actual = 'HELIX    1  H1 ILE A   23  GLU A   34  1                                  12    \n'
        print(repr(records[0]))
        print(repr(actual))
        self.assertEqual(records[0], actual)


    def test_het(self):
        """Test the generic_fns.structure.pdb_write.het() function."""

        # A dummy file to write to.
        file = DummyFileObject()

        # Create the PDB record.
        pdb_write.het(file, het_id='CA', chain_id='A', seq_num=1000, icode=None, num_het_atoms=1, text=None)

        # Test the record.
        records = file.readlines()
        actual = 'HET     CA  A1000       1                                                       \n'
        print(repr(records[0]))
        print(repr(actual))
        self.assertEqual(records[0], actual)


    def test_sheet(self):
        """Test the generic_fns.structure.pdb_write.sheet() function."""

        # A dummy file to write to.
        file = DummyFileObject()

        # Create the PDB record.
        pdb_write.sheet(file, strand=1, sheet_id='BET', num_strands=5, init_res_name='GLY', init_chain_id='A', init_seq_num=10, init_icode=None, end_res_name='VAL', end_chain_id='A', end_seq_num=17, end_icode=None, sense=0, cur_atom=None, cur_res_name=None, cur_chain_id=None, cur_res_seq=None, cur_icode=None, prev_atom=None, prev_res_name=None, prev_chain_id=None, prev_res_seq=None, prev_icode=None)

        # Test the record.
        records = file.readlines()
        actual = 'SHEET    1 BET 5 GLY A  10  VAL A  17  0                                        \n'
        print(repr(records[0]))
        print(repr(actual))
        self.assertEqual(records[0], actual)
