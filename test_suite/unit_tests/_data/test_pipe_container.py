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
from data.pipe_container import PipeContainer


class Test_pipe_container(TestCase):
    """Unit tests for the data.pipe_container relax module."""

    def setUp(self):
        """Create a data pipe structure for testing all the object methods."""

        # The initial empty structure.
        self.data_pipe = PipeContainer()


    def test_PipeContainer_is_empty(self):
        """Tests for the PipeContainer.is_empty() method."""

        # The newly initialised data pipe should be empty.
        self.assert_(self.data_pipe.is_empty())

        # Add an object.
        self.data_pipe.x = 1
        self.assert_(not self.data_pipe.is_empty())

        # Reset the data pipe, and modify an object.
        self.setUp()
        self.data_pipe.pipe_type = 'mf'
        self.assert_(not self.data_pipe.is_empty())

        # Reset the data pipe, and modify another object.
        self.setUp()
        self.data_pipe.mol[0].name = 'Ap4Aase'
        self.assert_(not self.data_pipe.is_empty())
