###############################################################################
#                                                                             #
# Copyright (C) 2007-2011 Edward d'Auvergne                                   #
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
from os import sep
import sys

# relax module imports.
import data; ds = data.Relax_data_store()
from test_suite.unit_tests.package_checking import PackageTestCase


class Empty_container:
    """An empty data container."""


class Test___init__(PackageTestCase):
    """Unit tests for the data.Relax_data_store class."""

    def setUp(self):
        """Set up a complex relax data store."""

        # Package info.
        self.package = data
        self.package_name = 'data'
        self.package_path = sys.path[0] + sep + 'data'
        
        # Add an empty data container as a new pipe.
        ds['empty'] = Empty_container()

        # Add an object to the empty data container.
        ds['empty'].x = 1

        # Add an object to the data store object.
        ds.test = 1


    def test_add(self):
        """Unit test for testing the addition of a new data pipe by the 'add()' method."""

        # Add a new data pipe.
        ds.add(pipe_name='new', pipe_type='mf')

        # Test that the new data pipe exists.
        self.assert_('new' in ds)


    def test_repr(self):
        """Unit test for the validity of the __repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(ds.__repr__()), str)


    def test_reset(self):
        """Unit test for the __reset__() class method."""

        # Execute the reset method.
        ds.__reset__()

        # Test that there are no keys.
        self.assertEqual(list(ds.keys()), [])

        # Test that the object ds.test is deleted.
        self.assert_(not hasattr(ds, 'test'))

        # Test that the object methods still exist.
        self.assert_(hasattr(ds, '__new__'))
        self.assert_(hasattr(ds, '__repr__'))
        self.assert_(hasattr(ds, '__reset__'))
        self.assert_(hasattr(ds, 'add'))

        # Test that the object's initial objects still exist.
        self.assert_(hasattr(ds, 'current_pipe'))
