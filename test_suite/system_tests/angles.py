###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
import sys
from unittest import TestCase

# relax module imports.
from data import Data as relax_data_store


class Angles(TestCase):
    """Class for testing the angle calculation function."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def test_angles(self):
        """The user function angles()."""

        # Read a PDB file.
        self.relax.interpreter._Structure.read_pdb(file='test.pdb', dir=sys.path[-1] + '/test_suite/system_tests/data', model=1)

        # Set the NH vector.
        self.relax.interpreter._Structure.vectors(heteronuc='N', proton='H')

        # Initialise a diffusion tensor.
        self.relax.interpreter._Diffusion_tensor.init((1.698e7, 1.417e7, 67.174, -83.718), param_types=3)

        # Calculate the angles.
        self.relax.interpreter._Angles.angles()
