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
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


class Structure(TestCase):
    """Class for testing the structural objects."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create('mf', 'mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_load_results(self):
        """Load the PDB file using the information in a results file."""

        # Path of the files.
        path = sys.path[-1] + '/test_suite/shared_data/results_files'

        # Read the results file.
        self.relax.interpreter._Results.read(file='str', dir=path)

        # Aliases.
        cdp = ds[ds.current_pipe]

        # Test the structure.
        self.assert_(hasattr(cdp, 'structure'))
        self.assertEqual(cdp.structure.file_name, 'Ap4Aase_res1-12.pdb')
        self.assert_(cdp.structure.path, '../structures')

