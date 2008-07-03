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
from data import Relax_data_store; ds = Relax_data_store()


class Results(TestCase):
    """TestCase class for the functional tests for the relax results files."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.relax.interpreter._Pipe.create('test', 'relax_fit')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_write_empty_results(self):
        """Test the writing of an empty results file."""

        # Write the results.
        self.relax.interpreter._Results.write(file="devnull")
