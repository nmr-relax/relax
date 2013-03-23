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

# Python module imports.
from unittest import TestCase

# relax module imports.
from lib import regex


class Test_regex(TestCase):
    """Unit tests for the functions of the 'lib.regex' module."""

    # Place the lib.regex module into the class namespace.
    regex = regex


    def test_search(self):
        """Test the proper behaviour of the lib.regex.search() function."""

        # Test a number of calls which should return True.
        self.assertEqual(True, self.regex.search('H', 'H'))
        self.assertEqual(True, self.regex.search('H*', 'H'))
        self.assertEqual(True, self.regex.search('H*', 'H1'))
        self.assertEqual(True, self.regex.search('H1', 'H1'))
        self.assertEqual(True, self.regex.search('^H*', 'H'))
        self.assertEqual(True, self.regex.search('^H*$', 'H'))
        self.assertEqual(True, self.regex.search('^H*$', 'H'))

        # Test a number of calls which should return False.
        self.assertEqual(False, self.regex.search('H*', 'NH'))
        self.assertEqual(False, self.regex.search('H', 'HN'))
        self.assertEqual(False, self.regex.search('H', 'H1'))
