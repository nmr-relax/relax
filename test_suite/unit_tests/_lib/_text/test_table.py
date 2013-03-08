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
from lib.text.table import format_table, MULTI_COL


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
        table_lines = table.split('\n')

        # The true table.
        true_table = [
            " _____________________ ",
            "                       ",
            "  Column 1   Column 2  ",
            " _____________________ ",
            "                       ",
            "  A          2         ",
            "  B          2         ",
            " _____________________ ",
            "                       ",
            ""    # This is because split combined with a final \n character.
        ]

        # Printout.
        print("The formatted table:")
        for i in range(len(table_lines)):
            print("'%s'" % table_lines[i])
        print("\nWhat the table should look like:")
        for i in range(len(true_table)):
            print("'%s'" % true_table[i])

        # Check the table.
        self.assertEqual(len(true_table), len(table_lines))
        for i in range(len(table_lines)):
            self.assertEqual(true_table[i], table_lines[i])


    def test_format_table2(self):
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
        table_lines = table.split('\n')

        # The true table.
        true_table = [
            " _____________________ ",
            "                       ",
            "  Column 1   Column 2  ",
            " _____________________ ",
            "                       ",
            "  A          2         ",
            "                       ",
            "  B          2         ",
            " _____________________ ",
            "                       ",
            ""    # This is because split combined with a final \n character.
        ]

        # Printout.
        print("The formatted table:")
        for i in range(len(table_lines)):
            print("'%s'" % table_lines[i])
        print("\nWhat the table should look like:")
        for i in range(len(true_table)):
            print("'%s'" % true_table[i])

        # Check the table.
        self.assertEqual(len(true_table), len(table_lines))
        for i in range(len(table_lines)):
            self.assertEqual(true_table[i], table_lines[i])


    def test_format_table3(self):
        """Test 3 of the lib.text.table.format_table() function."""

        # The table data.
        headings = [
            ['', 'Long text span test', MULTI_COL],
            ['Column 1', 'Column 2', 'Column 3']
        ]
        contents = [
            ['A', '2', '3.456'],
            ['B', '2', '4.567']
        ]

        # Create the table.
        table = format_table(headings=headings, contents=contents, spacing=True)
        table_lines = table.split('\n')

        # The true table.
        true_table = [
            " ________________________________ ",
            "                                  ",
            "             Long text span test  ",
            "                                  ",
            "  Column 1   Column 2   Column 3  ",
            " ________________________________ ",
            "                                  ",
            "  A          2          3.456     ",
            "                                  ",
            "  B          2          4.567     ",
            " ________________________________ ",
            "                                  ",
            ""    # This is because split combined with a final \n character.
        ]

        # Printout.
        print("The formatted table:")
        for i in range(len(table_lines)):
            print("'%s'" % table_lines[i])
        print("\nWhat the table should look like:")
        for i in range(len(true_table)):
            print("'%s'" % true_table[i])

        # Check the table.
        self.assertEqual(len(true_table), len(table_lines))
        for i in range(len(table_lines)):
            self.assertEqual(true_table[i], table_lines[i])


    def test_format_table4(self):
        """Test 4 of the lib.text.table.format_table() function."""

        # The table data.
        headings = [
            [None, 'Long text span test', MULTI_COL, MULTI_COL],
            ['Column 1', 'Column 2', 'Column 3', 'Column 4']
        ]
        contents = [
            ['A', 2, 3.4561234124, list],
            ['B', 2, 4.567745674, 1e-6]
        ]

        # Create the table.
        table = format_table(headings=headings, contents=contents, spacing=True, custom_format=[None, None, '%.3f', None])
        table_lines = table.split('\n')

        # The true table.
        true_table = [
            " ________________________________________________ ",
            "                                                  ",
            "             Long text span test                  ",
            "                                                  ",
            "  Column 1   Column 2   Column 3   Column 4       ",
            " ________________________________________________ ",
            "                                                  ",
            "  A                 2      3.456   <type 'list'>  ",
            "                                                  ",
            "  B                 2      4.568           1e-06  ",
            " ________________________________________________ ",
            "                                                  ",
            ""    # This is because split combined with a final \n character.
        ]

        # Printout.
        print("The formatted table:")
        for i in range(len(table_lines)):
            print("'%s'" % table_lines[i])
        print("\nWhat the table should look like:")
        for i in range(len(true_table)):
            print("'%s'" % true_table[i])

        # Check the table.
        self.assertEqual(len(true_table), len(table_lines))
        for i in range(len(table_lines)):
            self.assertEqual(true_table[i], table_lines[i])
