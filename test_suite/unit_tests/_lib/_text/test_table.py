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
            ['A', 2, 3.4561234124, [1,2.0]],
            ['B', 2, 4.567745674, 1e-6]
        ]

        # Create the table.
        table = format_table(headings=headings, contents=contents, spacing=True, custom_format=[None, None, '%.3f', None])
        table_lines = table.split('\n')

        # The true table.
        true_table = [
            " ___________________________________________ ",
            "                                             ",
            "             Long text span test             ",
            "                                             ",
            "  Column 1   Column 2   Column 3   Column 4  ",
            " ___________________________________________ ",
            "                                             ",
            "  A                 2      3.456   [1, 2.0]  ",
            "                                             ",
            "  B                 2      4.568      1e-06  ",
            " ___________________________________________ ",
            "                                             ",
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


    def test_format_table5(self):
        """Test 5 of the lib.text.table.format_table() function - no headings."""

        # The table data.
        contents = [
            ['A', 2],
            ['B', 2]
        ]

        # Create the table.
        table = format_table(contents=contents)
        table_lines = table.split('\n')

        # The true table.
        true_table = [
            " _______ ",
            "         ",
            "  A   2  ",
            "  B   2  ",
            " _______ ",
            "         ",
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


    def test_format_table6(self):
        """Test 6 of the lib.text.table.format_table() function - no headings."""

        # The table data.
        headings = [['Model', 'k', 'chi2', 'AIC', 'Average position', MULTI_COL, MULTI_COL, 'Motional eigenframe', MULTI_COL, MULTI_COL, 'Order parameters (deg)', MULTI_COL, MULTI_COL], [None, None, None, None, 'a', 'b', 'g', 'a', 'b/th', 'g/ph', 'thx', 'thy', 'smax']]
        contents = [['Rigid', 6, 1611.0583844357488, 1623.0583844357488, 2.7928187044509789, 6.241673451655573, 3.3350126302921255, None, None, None, None, None, None], ['Rotor', 9, 1393.0628812874404, 1411.0628812874404, 2.3720778521835015, 6.2511294411496241, 3.7347870727084764, None, 1.3782156252713658, 5.5998324326753401, None, None, 36.651271107544183], ['Iso cone, torsionless', 9, 1407.9014811061686, 1425.9014811061686, 2.2550248034078395, 6.2368882019396619, 3.891108977360032, None, 0.25090427716293384, 1.590485101074278, 21.287274572663485, None, None], ['Iso cone', 10, 1400.3558737738815, 1420.3558737738815, 2.8146957276396858, 6.2597080483925627, 3.2956149488567879, None, 1.3956123975976844, 5.5817149266639987, 10.300677006193942, None, 32.387495822632452], ['Pseudo ellipse, torsionless', 11, 1386.6214759007082, 1408.6214759007082, 2.6253119819082835, 6.2528446735668872, 3.4989380500907097, 2.692632830571366, 0.43833843941243616, 1.3038063115520346, 33.512494725673051, 15.888178532164503, None], ['Pseudo ellipse', 12, 1378.8893702060313, 1402.8893702060313, 2.7403158840045716, 6.259192518336242, 3.3759530521363121, 6.1651101516049849, 1.3600775439064279, 5.5851511636460813, 13.646328409458231, 0.74265383200964785, 31.027675419200627]]

        # Create the table.
        table = format_table(headings=headings, contents=contents, custom_format=[None, None, "%.2f", "%.2f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.3f", "%.2f", "%.2f", "%.2f"])
        table_lines = table.split('\n')

        # The true table.
        true_table = [
            " _______________________________________________________________________________________________________________________________ ",
            "                                                                                                                                 ",
            "  Model                         k    chi2      AIC       Average position        Motional eigenframe     Order parameters (deg)  ",
            "                                                         a       b       g       a       b/th    g/ph    thx     thy     smax    ",
            " _______________________________________________________________________________________________________________________________ ",
            "                                                                                                                                 ",
            "  Rigid                          6   1611.06   1623.06   2.793   6.242   3.335                                                   ",
            "  Rotor                          9   1393.06   1411.06   2.372   6.251   3.735           1.378   5.600                    36.65  ",
            "  Iso cone, torsionless          9   1407.90   1425.90   2.255   6.237   3.891           0.251   1.590   21.29                   ",
            "  Iso cone                      10   1400.36   1420.36   2.815   6.260   3.296           1.396   5.582   10.30            32.39  ",
            "  Pseudo ellipse, torsionless   11   1386.62   1408.62   2.625   6.253   3.499   2.693   0.438   1.304   33.51   15.89           ",
            "  Pseudo ellipse                12   1378.89   1402.89   2.740   6.259   3.376   6.165   1.360   5.585   13.65    0.74    31.03  ",
            " _______________________________________________________________________________________________________________________________ ",
            "                                                                                                                                 ",
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
