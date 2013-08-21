###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
from unittest import TestCase

# relax module imports.
from lib.io import DummyFileObject
from lib.spectrum.sparky import write_list


class Test_sparky(TestCase):
    """Unit tests for the lib.software.sparky relax module."""

    def test_write_list(self):
        """Test the lib.software.sparky.write_list() function."""

        # The data.
        res_names = ['LEU', 'GLY', 'SER', 'MET', 'TRP', 'TRP', 'ASN']
        res_nums = [3, 4, 5, 6, 40, 40, 55]
        atom1_names = ['N', 'N', 'N', 'N', 'N', 'NE1', 'N']
        atom2_names = ['HN', 'HN', 'HN', 'HN', 'HN', 'HE1', 'HN']
        w1 = [122.454, 111.978, 115.069, 120.910, 123.335, 130.204, 116.896]
        w2 = [8.397, 8.720, 8.177, 8.813, 8.005, 10.294, 7.468]
        heights = [2535, 5050, 51643, 53663, -65111, -181131, -105322]

        # The result.
        file_data = [
            '      Assignment         w1         w2   Data Height\n',
            '\n',
            '         LEU3N-HN    122.454      8.397         2535\n',
            '         GLY4N-HN    111.978      8.720         5050\n',
            '         SER5N-HN    115.069      8.177        51643\n',
            '         MET6N-HN    120.910      8.813        53663\n',
            '        TRP40N-HN    123.335      8.005       -65111\n',
            '     TRP40NE1-HE1    130.204     10.294      -181131\n',
            '        ASN55N-HN    116.896      7.468      -105322\n'
        ]

        # Write the data out.
        file = DummyFileObject()
        write_list(file_prefix=file, res_names=res_names, res_nums=res_nums, atom1_names=atom1_names, atom2_names=atom2_names, w1=w1, w2=w2, data_height=heights)

        # Check the file data.
        lines = file.readlines()
        self.assertEqual(len(lines), len(file_data))
        for i in range(len(lines)):
            self.assertEqual(lines[i], file_data[i])
