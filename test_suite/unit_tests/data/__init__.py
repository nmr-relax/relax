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

# Python module imports.
from unittest import TestCase

# relax module imports.
from data import Data


__all__ = ['test_diff_tensor',
           'test_mol_res_spin']



class NewStore(Data):
    """Subclass the relax data storage object for the isolation and creation of a new singleton."""


class Empty_container:
    """An empty data container."""


class Test_Data(TestCase):
    """Unit tests for the data.Data class."""

    def setUp(self):
        """Set up a complex relax data store."""

        # Create a new relax data store singleton.
        self.data_store = NewStore()

        # Add an empty data container as a new pipe.
        self.data_store['empty'] = Empty_container()

        # Add an object to the empty data container.
        self.data_store['empty'].x = 1

        # Add an object to the data store object.
        self.data_store.test = 1

        # Create a new reference.
        self.new_ref = NewStore()


    def tearDown(self):
        """Destroy the subclassed data store."""

        # Delete all references (which should decrement the singleton's ref counter to 0, hence destroying it).
        del self.new_ref
        del self.data_store


    def test_add(self):
        """Unit test for testing the addition of a new data pipe by the 'add()' method."""

        # Add a new data pipe.
        self.data_store.add('new')

        # Test that the new data pipe exists.
        self.assert_(self.data_store.has_key('new'))


    def test_repr(self):
        """Unit test for the validity of the __repr__() method."""

        # Test that __repr__() returns a string.
        self.assert_(type(self.data_store.__repr__()), str)


    def test_reset(self):
        """Unit test for the __reset__() class method."""

        # Execute the reset method.
        self.data_store.__reset__()

        # Test that there are no keys.
        self.assertEqual(self.data_store.keys(), [])

        # Test that the object self.data_store.test is deleted.
        self.assert_(not hasattr(self.data_store, 'test'))

        # Test that the object methods still exist.
        self.assert_(hasattr(self.data_store, '__new__'))
        self.assert_(hasattr(self.data_store, '__repr__'))
        self.assert_(hasattr(self.data_store, '__reset__'))
        self.assert_(hasattr(self.data_store, 'add'))

        # Test that the object's initial objects still exist.
        self.assert_(hasattr(self.data_store, 'current_pipe'))


    def test_singleton(self):
        """Test that the relax data storage object is functioning as a singleton."""

        # Test that the new reference to NewStore is the singleton instance reference.
        self.assertEqual(self.data_store, self.new_ref)

        # Delete all references (which should decrement the singleton's ref counter to 0, hence destroying it).
        del self.new_ref
        del self.data_store

        # Create a new singleton.
        new = NewStore()

        # Test that the object 'test' from the original singleton does not exist.
        self.assert_(not hasattr(new, 'test'))
