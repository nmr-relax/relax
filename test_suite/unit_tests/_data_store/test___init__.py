###############################################################################
#                                                                             #
# Copyright (C) 2007-2009,2024 Edward d'Auvergne                              #
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
from os import sep
import sys

# relax module imports.
import data_store
from data_store import Relax_data_store; ds = Relax_data_store()
from test_suite.unit_tests.package_checking import PackageTestCase


class Empty_container:
    """An empty data container."""


class Test___init__(PackageTestCase):
    """Unit tests for the data_store package."""

    def setUp(self):
        """Set up a complex relax data store."""

        # Package info.
        self.package = data_store
        self.package_name = 'data_store'
        self.package_path = sys.path[0] + sep + 'data_store'
        
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
        self.assertTrue('new' in ds)


    def test_repr(self):
        """Unit test for the validity of the __repr__() method."""

        # Test that __repr__() returns a string.
        self.assertTrue(type(ds.__repr__()), str)


    def test_reset(self):
        """Unit test for the __reset__() class method."""

        # Execute the reset method.
        ds.__reset__()

        # Test that there are no keys.
        self.assertEqual(list(ds.keys()), [])

        # Test that the object ds.test is deleted.
        self.assertTrue(not hasattr(ds, 'test'))

        # Test that the object methods still exist.
        self.assertTrue(hasattr(ds, '__new__'))
        self.assertTrue(hasattr(ds, '__repr__'))
        self.assertTrue(hasattr(ds, '__reset__'))
        self.assertTrue(hasattr(ds, 'add'))

        # Test that the object's initial objects still exist.
        self.assertTrue(hasattr(ds, 'current_pipe'))
