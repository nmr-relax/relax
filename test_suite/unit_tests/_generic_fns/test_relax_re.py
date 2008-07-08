###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
        self.assertTrue(self.relax_re_fns.search('H', 'H'))
        self.assertTrue(self.relax_re_fns.search('H*', 'H'))
        self.assertTrue(self.relax_re_fns.search('H*', 'H1'))
        self.assertTrue(self.relax_re_fns.search('H1', 'H1'))
        self.assertTrue(self.relax_re_fns.search('^H*', 'H'))
        self.assertTrue(self.relax_re_fns.search('^H*$', 'H'))
        self.assertTrue(self.relax_re_fns.search('^H*$', 'H'))

        # Test a number of calls which should return False.
        self.assertFalse(self.relax_re_fns.search('H*', 'NH'))
        self.assertFalse(self.relax_re_fns.search('H', 'HN'))
        self.assertFalse(self.relax_re_fns.search('H', 'H1'))
