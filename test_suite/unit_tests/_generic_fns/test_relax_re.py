###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
from generic_fns import relax_re


class Test_relax_re(TestCase):
    """Unit tests for the functions of the 'generic_fns.relax_re' module."""

    # Place the generic_fns.relax_re module into the class namespace.
    relax_re_fns = relax_re


    def test_search(self):
        """Test the proper behaviour of the generic_fns.relax_re.search() function."""

        # Test a number of calls which should return True.
        self.assertEqual(True, self.relax_re_fns.search('H', 'H'))
        self.assertEqual(True, self.relax_re_fns.search('H*', 'H'))
        self.assertEqual(True, self.relax_re_fns.search('H*', 'H1'))
        self.assertEqual(True, self.relax_re_fns.search('H1', 'H1'))
        self.assertEqual(True, self.relax_re_fns.search('^H*', 'H'))
        self.assertEqual(True, self.relax_re_fns.search('^H*$', 'H'))
        self.assertEqual(True, self.relax_re_fns.search('^H*$', 'H'))

        # Test a number of calls which should return False.
        self.assertEqual(False, self.relax_re_fns.search('H*', 'NH'))
        self.assertEqual(False, self.relax_re_fns.search('H', 'HN'))
        self.assertEqual(False, self.relax_re_fns.search('H', 'H1'))
