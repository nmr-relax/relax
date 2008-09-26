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
from generic_fns import results, structure
from specific_fns.model_free import main


class Test_main(TestCase):
    """Unit tests for the class methods of specific_fns.model_free.main.Model_free_main."""

    # Instantiate the class.
    inst = main.Model_free_main()


    def setUp(self):
        """Setup some structures for the unit tests."""

        # Create a model-free data pipe.
        ds.add(pipe_name='orig', pipe_type='mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_duplicate_data1(self):
        """Test the model-free duplicate_data() method."""

        # Duplicate the data.
        self.inst.duplicate_data('orig', 'new', model_index=0)


    def test_duplicate_data2(self):
        """Test the model-free duplicate_data() method."""

        # Read a model-free results file.
        results.read(file='final_results_trunc_1.3', directory=sys.path[-1] + '/test_suite/shared_data/model_free/OMP')

        # Duplicate the data.
        self.inst.duplicate_data('orig', 'new', model_index=0)


    def test_duplicate_data3(self):
        """Test the model-free duplicate_data() method."""

        # Read a model-free results file.
        results.read(file='final_results_trunc_1.3', directory=sys.path[-1] + '/test_suite/shared_data/model_free/OMP')

        # Load a structure.
        structure.main.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + '/test_suite/shared_data/structures', model=1, parser='internal')

        # Duplicate the data.
        self.inst.duplicate_data('orig', 'new', model_index=0)

        # Check the original data.
        self.assert_(hasattr(ds['orig'], 'structure'))

        # Check the duplication.
        self.assert_(hasattr(ds['new'], 'structure'))
