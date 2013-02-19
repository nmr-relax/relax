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
        """Test the pdb_read.atom() function."""

        # Parse a PDB record.
        record = pdb_read.atom('ATOM    158  CG  GLU    11       9.590  -1.041 -11.596  1.00  0.00           C')

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
