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
from generic_fns.structure import pdb_read
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_pdb_read(UnitTestCase):
    """Unit tests for the functions of the 'generic_fns.structure.pdb_read' module."""

    def test_atom(self):
        """Test the generic_fns.structure.pdb_read.atom() function."""

        # Parse a PDB record.
        record = pdb_read.atom('ATOM    158  CG  GLU    11       9.590  -1.041 -11.596  1.00  0.00           C  ')

        # Test the elements.
        self.assertEqual(record[0], 'ATOM')
        self.assertEqual(record[1], 158)
        self.assertEqual(record[2], 'CG')
        self.assertEqual(record[3], None)
        self.assertEqual(record[4], 'GLU')
        self.assertEqual(record[5], None)
        self.assertEqual(record[6], 11)
        self.assertEqual(record[7], None)
        self.assertEqual(record[8], 9.59)
        self.assertEqual(record[9], -1.041)
        self.assertEqual(record[10], -11.596)
        self.assertEqual(record[11], 1.0)
        self.assertEqual(record[12], 0.0)
        self.assertEqual(record[13], 'C')
        self.assertEqual(record[14], None)


    def test_helix(self):
        """Test the generic_fns.structure.pdb_read.helix() function."""

        # Parse a PDB record (from the 1UBQ PDB file).
        record = pdb_read.helix('HELIX    1  H1 ILE A   23  GLU A   34  1                                  12    ')

        # Test the elements.
        self.assertEqual(record[0], 'HELIX')
        self.assertEqual(record[1], 1)
        self.assertEqual(record[2], 'H1')
        self.assertEqual(record[3], 'ILE')
        self.assertEqual(record[4], 'A')
        self.assertEqual(record[5], 23)
        self.assertEqual(record[6], None)
        self.assertEqual(record[7], 'GLU')
        self.assertEqual(record[8], 'A')
        self.assertEqual(record[9], 34)
        self.assertEqual(record[10], None)
        self.assertEqual(record[11], 1)
        self.assertEqual(record[12], None)
        self.assertEqual(record[13], 12)


    def test_sheet(self):
        """Test the generic_fns.structure.pdb_read.sheet() function."""

        # Parse a PDB record (from the 1UBQ PDB file).
        record = pdb_read.sheet('SHEET    1 BET 5 GLY A  10  VAL A  17  0                                        ')

        # Test the elements.
        self.assertEqual(record[0], 'SHEET')
        self.assertEqual(record[1], 1)
        self.assertEqual(record[2], 'BET')
        self.assertEqual(record[3], 5)
        self.assertEqual(record[4], 'GLY')
        self.assertEqual(record[5], 'A')
        self.assertEqual(record[6], 10)
        self.assertEqual(record[7], None)
        self.assertEqual(record[8], 'VAL')
        self.assertEqual(record[9], 'A')
        self.assertEqual(record[10], 17)
        self.assertEqual(record[11], None)
        self.assertEqual(record[12], 0)
        self.assertEqual(record[13], None)
        self.assertEqual(record[14], None)
        self.assertEqual(record[15], None)
        self.assertEqual(record[16], None)
        self.assertEqual(record[17], None)
        self.assertEqual(record[18], None)
        self.assertEqual(record[19], None)
        self.assertEqual(record[20], None)
        self.assertEqual(record[21], None)
        self.assertEqual(record[22], None)
