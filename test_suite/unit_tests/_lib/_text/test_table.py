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
from lib.text.table import format_table


class Test_table(TestCase):
    """Unit tests for the lib.text.table relax module."""

    def test_format_table1(self):
        """Test 1 of the lib.text.table.format_table() function."""

        # The table data.
        headings = [
            ['Column 1', 'Column 2']
        ]
        contents = [
            ['A', '2'],
            ['B', '2']
        ]

        # Create the table.
        table = format_table(headings=headings, contents=contents)


    def test_format_table1(self):
        """Test 2 of the lib.text.table.format_table() function."""

        # The table data.
        headings = [
            ['Column 1', 'Column 2']
        ]
        contents = [
            ['A', '2'],
            ['B', '2']
        ]

        # Create the table.
        table = format_table(headings=headings, contents=contents, max_width=30, spacing=True, debug=True)
