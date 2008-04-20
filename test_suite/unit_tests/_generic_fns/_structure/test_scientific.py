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
from data import Data as relax_data_store
from generic_fns.structure.scientific import Scientific_data


class Test_scientific(TestCase):
    """Unit tests for the functions of the 'generic_fns.structure.scientific' module."""

    def setUp(self):
        """Set up for all the Scientific Python PDB structural object unit tests."""

        # Instantiate the structural data object.
        self.data = Scientific_data()


    def tearDown(self):
        """Reset the relax data storage object."""

        # Delete the structural data object.
        del self.data

        # Reset.
        relax_data_store.__reset__()


    def test_load_structures(self):
        """Test the loading of a PDB file.

        This tests the Scientific_data.load_structures() method.
        """

        # Load the PDB file.
        self.data.load_structures()
