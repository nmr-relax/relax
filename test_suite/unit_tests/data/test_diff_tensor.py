#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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

from os.path import join, sep
from string import split
from sys import path
from unittest import TestCase, main

# Modify the system path so that the relax modules can be imported (for stand alone execution).
path_comps = split(path[0], sep)
relax_path = sep + join(*path_comps[0:5])
path.append(relax_path)

from data.diff_tensor import DiffTensorElement


# Tests for the data.diff_tensor module.
class Test_diff_tensor(TestCase):
    def setUp(self):
        """Set 'self.diff_data' to an empty instance of the DiffTensorElement class."""

        self.diff_data = DiffTensorElement()


    def test_set_Diso(self):
        """Test that the Diso parameter cannot be set."""

        # Assert that a RelaxError occurs when Diso is set (to the tm value of 10 ns).
        self.assertRaises(RelaxError, setattr, self.diff_data, 'Diso', 1/(6*1e-8))

        # Make sure that the Diso parameter has not been set.
        self.assert_(not hasattr(self.diff_data, 'Diso'))


    def test_set_tm(self):
        """Test the setting of the tm parameter.
        
        The setting of the tm parameter should automatically create the Diso parameter.
        """

        # Set the tm value to 10 ns.
        self.diff_data.tm = 1e-8

        # Test that the tm parameter has been set correctly.
        self.assert_(hasattr(self.diff_data, 'tm'))
        self.assertEqual(self.diff_data.tm, 1e-8)

        # Test that the Diso parameter has been set correctly.
        self.assert_(hasattr(self.diff_data, 'Diso'))
        self.assertEqual(self.diff_data.Diso, 1/(6*1e-8))


if __name__ == '__main__':
    main()
